import logging
import stripe
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.wallet.models import (
    Wallet,
    Transaction,
    TransactionType,
    TransactionStatus,
    PaymentMethod,
    PaymentProvider,
    BankTransferDetails,
    TransactionLog,
)


from .constants import (
    TransactionStatusConstant,
    PaymentMethodConstant,
    PaymentProviderConstant,
    TransactionTypeConstant,
)
from .serializers import (
    WalletSerializer,
    BankTransactionSerializer,
    BankTransferDetailsSerializer,
)


# get Stripe API key from env file
from .utils import calculate_order_amount

# import env variable from settings.py
from django.conf import settings

# initialize
env = settings.ENVIRONMENT
stripe.api_key = env("STRIPE_SECRET_KEY_DEV")
logger = logging.getLogger(__name__)


# --- ViewSets
class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    @action(
        detail=False,
        methods=["get"],
        # url_path with user_id having a regex format for UUID, matches 32 hexadecimal digits with hyphens
        url_path="user/(?P<user_id>[0-9a-f-]{36})",
        permission_classes=[IsAdminUser],
    )
    def get_balance_by_user_id(self, request, *args, **kwargs):
        """
        Get wallet balance by user id. We will retrieve specific attributes from the wallet object.

        """
        # get single object by user id, if it doesn't exist, return HTTP 404 as the response
        user_id = kwargs.get("user_id")
        user_wallet = get_object_or_404(Wallet, user_id=user_id)

        # Return it
        return Response(user_wallet.balance)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"wallet/(?P<wallet_id>\d+)",
        permission_classes=[IsAdminUser],
    )
    def get_balance_by_wallet_id(self, request, *args, **kwargs):
        """

        Get wallet balance by wallet id. We will retrieve specific attributes from the wallet object.

        """

        # get single object by wallet id, if it doesn't exist, return HTTP 404 as the response
        wallet_id = kwargs.get("wallet_id")
        user_wallet = get_object_or_404(Wallet, id=wallet_id)

        # Return it
        return Response(user_wallet.balance)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"wallet",
        permission_classes=[IsAuthenticated],
    )
    def get_wallet_by_user_id(self, request):
        """

        Get wallet object by authenticated user. We will retrieve specific attributes from the wallet object.

        """

        # get single object by user id, if it doesn't exist, return HTTP 404 as the response
        user_id = request.user.id
        user_wallet = get_object_or_404(Wallet, user_id=user_id)
        serializer = WalletSerializer(user_wallet)

        # Return it
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"create-checkout-session/(?P<amount_to_add>\d+)",
        permission_classes=[IsAuthenticated],
    )
    def create_checkout_session(self, request, pk=None, amount_to_add=None):
        # if the amount is bigger than 400, return error
        # NOTE: consider adjusting for each currency (e.g. 400 USD, 400 EUR, 400 Argentine Peso, etc.)
        if int(amount_to_add) > 400:
            return Response(
                {"error": "Amount to add cannot be bigger than 400"}, 400
            )

        # get input data
        wallet_detail = get_object_or_404(Wallet, id=pk)
        # get additional required data
        transaction_type = TransactionType.objects.get(
            title=TransactionTypeConstant.DEPOSIT
        )
        transaction_status = TransactionStatus.objects.get(
            title=TransactionStatusConstant.PENDING
        )
        payment_method = PaymentMethod.objects.get(
            title=PaymentMethodConstant.ALL
        )
        payment_provider = PaymentProvider.objects.get(
            title=PaymentProviderConstant.STRIPE
        )
        # new transaction
        transaction = Transaction.objects.create(
            wallet=wallet_detail,
            type=transaction_type,
            status=transaction_status,
            payment_method=payment_method,
            payment_provider=payment_provider,
            amount_paid=amount_to_add,
            currency=wallet_detail.currency,
        )

        # define base url based on DEBUG variable in env file
        base_url = (
            env("BASE_URL_DEV") if env("DJANGO_DEBUG") else env("BASE_URL_PROD")
        )
        success_url = "{}{}".format(
            base_url,
            reverse(
                "wallet-successful-stripe-payment",
                kwargs={"transaction_id": transaction.id},
            ),
        )
        cancel_url = "{}{}".format(
            base_url,
            reverse(
                "wallet-failed-stripe-payment",
                kwargs={"transaction_id": transaction.id},
            ),
        )
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Agrega dinero a tu cuenta",
                        },
                        "unit_amount": calculate_order_amount(
                            int(amount_to_add)
                        ),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        # if the session was created successfully, create a new Transaction object
        if session.url:
            # create a new Transaction object
            transaction.save()

            # logging
            logger.debug(
                "A new Stripe checkout session was created successfully. The transaction ID is {} and the "
                "status of the transaction is PENDING".format(transaction.id)
            )
            transaction_log = TransactionLog.objects.create(
                transaction=transaction,
                reason="A new Stripe checkout session was created successfully",
                new_status=transaction.status,
                changed_by="",
            )
            transaction_log.save()

        return Response(session.url)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"stripe/success/(?P<transaction_id>\d+)",
    )
    def successful_stripe_payment(self, request, *args, **kwargs):
        """
        This endpoint is called when the user successfully completes the payment flow on Stripe.
        """

        # get single object by wallet id, if it doesn't exist, return HTTP 404 as the response
        transaction_id = kwargs.get("transaction_id")
        transaction = get_object_or_404(Transaction, id=transaction_id)
        user_wallet = get_object_or_404(Wallet, id=transaction.wallet.id)

        # update wallet balance
        user_wallet.balance = user_wallet.balance + transaction.amount_paid
        user_wallet.save()

        # update transaction status
        transaction.status = TransactionStatus.objects.get(
            title=TransactionStatusConstant.COMPLETED
        )
        transaction.save()

        # update logs
        logger.info(
            "The transaction with ID {} was completed successfully".format(
                transaction.id
            )
        )
        transaction_log = TransactionLog.objects.get(transaction=transaction)
        transaction_log.reason = (
            "The transaction with ID {} was completed successfully".format(
                transaction.id
            )
        )
        transaction_log.prev_status = transaction_log.new_status
        transaction_log.new_status = transaction.status
        transaction_log.save()

        # return
        return Response("The payment was successful")

    @action(
        detail=False,
        methods=["get"],
        url_path=r"stripe/cancel/(?P<transaction_id>\d+)",
    )
    def failed_stripe_payment(self, request, *args, **kwargs):
        """
        This endpoint is called when a user cancels a payment by triggering a button to "go back" on Stripe.
        """

        # get single object by wallet id, if it doesn't exist, return HTTP 404 as the response
        transaction_id = kwargs.get("transaction_id")
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # update transaction status
        transaction.status = TransactionStatus.objects.get(title="Cancelled")
        transaction.save()

        # update logs
        logger.info(
            "The transaction with ID {} was cancelled".format(transaction.id)
        )
        transaction_log = TransactionLog.objects.get(transaction=transaction)
        transaction_log.reason = (
            "The transaction with ID {} was cancelled".format(transaction.id)
        )
        transaction_log.prev_status = transaction_log.new_status
        transaction_log.new_status = transaction.status
        transaction_log.save()

        return Response("The payment failed")

    @action(
        detail=False,
        methods=["get"],
        url_path=r"bank-transfer/(?P<amount_to_pay>\d+)",
        permission_classes=[IsAuthenticated],
    )
    def get_bank_transfer_details(self, request, amount_to_pay):
        """
        Get bank transfer details by authenticated user.
        """

        # replace above with serializer
        bank_transfer_object = BankTransferDetails.objects.get(
            bank_name="Banco Santander", account_name="One Saw SA"
        )
        bank_transfer_details_serializer = BankTransferDetailsSerializer(
            bank_transfer_object
        )

        # Return it
        return Response(bank_transfer_details_serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"bank-transfer/confirm",
        permission_classes=[IsAuthenticated],
        serializer_class=BankTransactionSerializer,
    )
    def confirm_bank_transfer_payment(self, request, pk):
        """
        We will save the details a moderator can use to confirm bank transfer payment by authenticated user.
        """

        # get data to create a new transaction object
        user_wallet = get_object_or_404(Wallet, pk=pk)
        bank_serializer = BankTransactionSerializer(data=request.data)
        payment_method = PaymentMethod.objects.get(
            title=PaymentMethodConstant.BANK_TRANSFER
        )
        payment_provider = PaymentProvider.objects.get(
            title=PaymentProviderConstant.BANK
        )
        transaction_status = TransactionStatus.objects.get(
            title=TransactionStatusConstant.PENDING
        )
        transaction_type = TransactionType.objects.get(
            title=TransactionTypeConstant.DEPOSIT
        )

        if bank_serializer.is_valid():
            # create new transaction
            transaction_object = Transaction.objects.create(
                amount_paid=bank_serializer.validated_data["amount_paid"],
                payment_account_number=bank_serializer.validated_data[
                    "payment_account_number"
                ],
                reference_code=bank_serializer.validated_data["reference_code"],
                created_at=bank_serializer.validated_data["transaction_date"],
                notes="bank name: {}, sender/recipient info: {}, transaction description: {}".format(
                    bank_serializer.validated_data["bank_name"],
                    bank_serializer.validated_data["sender_recipient_info"],
                    bank_serializer.validated_data["transaction_description"],
                ),
                type=transaction_type,
                status=transaction_status,
                payment_method=payment_method,
                payment_provider=payment_provider,
                wallet=user_wallet,
                currency=user_wallet.currency,
            )
            transaction_object.save()

            # create a new TransactionLog object
            transaction_log = TransactionLog.objects.create(
                transaction=transaction_object,
                reason="A new transaction was created successfully with: bank name: {}, sender/recipient "
                "info: {}".format(
                    bank_serializer.validated_data["bank_name"],
                    bank_serializer.validated_data["sender_recipient_info"],
                ),
                new_status=transaction_object.status,
                changed_by="",
                created_at=bank_serializer.validated_data["transaction_date"],
            )
            transaction_log.save()

            # logging
            logger.info(
                "A new bank transaction was created successfully with the following details {}".format(
                    bank_serializer.validated_data
                ),
            )

            return Response(
                "The transaction details were saved successfully and are going to be reviewed by a "
                "moderator"
            )

        return Response(bank_serializer.errors, status=400)


# --- Views
# add "wallet_id" as an URL parameter
def custom_button_view(request, wallet_id):
    print("WALLET ID IS:", wallet_id)

    # Your custom button logic goes here
    # This is just a placeholder example
    return render(request, "admin/custom_button.html")
