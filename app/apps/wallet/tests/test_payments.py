import pytest
from django.contrib.auth import get_user_model
from apps.wallet.models import (
    Wallet,
    Currency,
    Transaction,
    TransactionStatus,
    PaymentMethod,
    PaymentProvider,
    TransactionType,
    TransactionLog,
    TransactionApproval,
    BankTransferDetails,
)
from django.urls import reverse

from app.apps.wallet.constants import (
    TransactionStatusConstant,
    PaymentMethodConstant,
    PaymentProviderConstant,
    TransactionTypeConstant,
)


# ------------------ Stripe ------------------
@pytest.fixture(scope="function")
@pytest.mark.django_db
def setup_test_data():
    # NOTE: this method is called before each test
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email="regular@user.com",
        password="foo",
        first_name="Normal",
        last_name="User",
        is_staff=True,
    )
    currency = Currency.objects.create(title="USD", symbol="$")
    wallet = Wallet.objects.create(
        user_id=user.id, balance=2000, currency=currency
    )

    transaction_status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.PENDING
    )
    payment_method = PaymentMethod.objects.create(
        title=PaymentMethodConstant.ALL
    )
    payment_provider = PaymentProvider.objects.create(
        title=PaymentProviderConstant.STRIPE
    )
    transaction_type = TransactionType.objects.create(
        title=TransactionTypeConstant.DEPOSIT
    )

    # create a new Transaction object with the status "Pending"
    transaction = Transaction.objects.create(
        wallet=wallet,
        type=transaction_type,
        status=transaction_status,
        payment_method=payment_method,
        payment_provider=payment_provider,
        amount_paid=100,
        currency=wallet.currency,
    )

    return user, wallet, transaction


@pytest.mark.django_db
def test_create_checkout_session(client, setup_test_data):
    """
    Test the creation of a checkout session via Stripe. When the user wants to add money to their balance, they can do
    so by hitting an endpoint that creates a checkout session. This session is then used to redirect the user to the
    Stripe checkout page, where they can pay for the amount they want to add to their balance. This test checks that
    the checkout session is created successfully.
    """
    # required data
    user, wallet, transaction = setup_test_data

    # authenticate user
    client.post(
        "/auth/login/",
        {"email": user.email, "password": "foo"},
        format="json",
    )

    # init
    amount = 100
    # make request
    url = reverse(
        "wallet-create-checkout-session",
        kwargs={"amount_to_add": amount, "pk": wallet.id},
    )
    response = client.get(url, format="json")

    # assertions
    assert response.status_code == 200
    assert response.data is not None
    assert TransactionLog.objects.get(
        reason="A new Stripe checkout session was created successfully"
    )


@pytest.mark.django_db
def test_success_url_works_properly(client, setup_test_data):
    """
    Test that the success url works properly. When the user pays for the amount they want to add to their balance,
    they are redirected to the success url and the system updates the Transaction status and the Payment status.
     This test checks that the success url works properly.
    """
    # required data
    user, wallet, transaction = setup_test_data
    # expected data
    amount_to_add = 100
    expected_amount = wallet.balance + amount_to_add

    # create the transaction status "Completed", so that it can we used in the function to test
    transaction_status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.COMPLETED
    )

    # create new TransactionLog object
    transaction_log = TransactionLog.objects.create(
        transaction=transaction, new_status=transaction_status
    )
    # save the object
    transaction_log.save()

    # make request
    url = reverse(
        "wallet-successful-stripe-payment",
        kwargs={"transaction_id": transaction.id},
    )
    response = client.get(url, format="json")
    # assertions
    assert response.status_code == 200
    assert response.data is not None
    assert Wallet.objects.get(user=user).balance == expected_amount
    assert (
        TransactionLog.objects.get(transaction=transaction).new_status.title
        == TransactionStatusConstant.COMPLETED
    )
    assert (
        Transaction.objects.get(wallet=wallet).status.title
        == TransactionStatusConstant.COMPLETED
    )


@pytest.mark.django_db
def test_cancel_url_works_properly(client, setup_test_data):
    """
    Test that the cancel url works properly. When the user cancels the payment, they are redirected to the cancel
    url and the system updates the Transaction status and the Payment status. This test checks that the cancel url
    works properly.
    """
    # required data
    _, wallet, transaction = setup_test_data

    # create the transaction status "Cancelled", so that it can we used in the function to test
    transaction_status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.CANCELLED
    )

    # create new TransactionLog object
    transaction_log = TransactionLog.objects.create(
        transaction=transaction, new_status=transaction_status
    )
    # save the object
    transaction_log.save()

    # make request
    url = reverse(
        "wallet-failed-stripe-payment",
        kwargs={"transaction_id": transaction.id},
    )
    response = client.get(url, format="json")
    # assertions
    assert response.status_code == 200
    assert response.data is not None
    assert (
        TransactionLog.objects.get(transaction=transaction).new_status.title
        == "Cancelled"
    )
    assert (
        Transaction.objects.get(wallet=wallet).status.title
        == TransactionStatusConstant.CANCELLED
    )


# ------------------ Bank Transfer ------------------
@pytest.mark.django_db
def test_get_bank_transfer_details(client, setup_test_data):
    """
    This test checks that the bank transfer details are returned successfully.
    """
    # required data
    user, _, _ = setup_test_data

    # expected data
    amount_to_pay = 100
    expected_bank_details = {
        "bank_name": "Banco Santander",
        "account_name": "One Saw SA",
        "account_number": "0298977",
        "CBU": "0720166620000002989772",
        "branch": "166",
        "alias": "ONE.XP CUIT: 30-71069775-9",
        "amount": str(amount_to_pay),
    }

    # create a new BankTransfer object with details
    BankTransferDetails.objects.create(
        bank_name=expected_bank_details["bank_name"],
        account_name=expected_bank_details["account_name"],
        account_number=expected_bank_details["account_number"],
        CBU=expected_bank_details["CBU"],
        branch=expected_bank_details["branch"],
        alias=expected_bank_details["alias"],
    )
    # authentication
    client.post(
        "/auth/login/",
        {"email": user.email, "password": "foo"},
        format="json",
    )

    # make request
    url = reverse(
        "wallet-get-bank-transfer-details",
        kwargs={"amount_to_pay": amount_to_pay},
    )
    response = client.get(url, format="json")

    # assertions
    assert response.status_code == 200
    assert response.data["bank_name"] == expected_bank_details["bank_name"]
    assert (
        response.data["account_name"] == expected_bank_details["account_name"]
    )
    assert (
        response.data["account_number"]
        == expected_bank_details["account_number"]
    )
    assert response.data["CBU"] == expected_bank_details["CBU"]
    assert response.data["branch"] == expected_bank_details["branch"]
    assert response.data["alias"] == expected_bank_details["alias"]


@pytest.mark.django_db
def test_confirm_bank_transfer_payment(client, setup_test_data):
    """
    This test checks that the bank transfer payment details are saved correctly for review and that new TransactionLog
    and Transaction objects are created successfully.
    """

    # required data
    user, wallet, _ = setup_test_data
    # create payment method "Bank Transfer" and the payment provider "Bank"
    PaymentMethod.objects.create(title=PaymentMethodConstant.BANK_TRANSFER)
    PaymentProvider.objects.create(title=PaymentProviderConstant.BANK)

    # expected data
    amount_to_pay = 100
    expected_transaction_reference_code = "123456789"
    expected_transaction_payment_account_number = "0298977"
    bank_name = "Banco Santander"
    sender_recipient_info = "John Doe"
    transaction_log_reason = (
        "A new transaction was created successfully with: bank name: {}, "
        "sender/recipient info: {}".format(bank_name, sender_recipient_info)
    )
    bank_payment_data = {
        "amount_paid": amount_to_pay,
        "payment_account_number": expected_transaction_payment_account_number,
        "reference_code": expected_transaction_reference_code,
        "transaction_date": "2021-08-10T12:00:00Z",
        "sender_recipient_info": sender_recipient_info,
        "transaction_description": "Payment for services",
        "bank_name": bank_name,
    }

    # authentication
    client.post(
        "/auth/login/",
        {"email": user.email, "password": "foo"},
        format="json",
    )

    # make request
    url = reverse(
        "wallet-confirm-bank-transfer-payment",
        kwargs={"pk": wallet.id},
    )
    response = client.post(url, bank_payment_data, format="json")

    # assertions
    assert response.status_code == 200
    assert (
        response.data
        == "The transaction details were saved successfully and are going to be reviewed by a "
        "moderator"
    )
    assert TransactionLog.objects.get(reason=transaction_log_reason)
    assert Transaction.objects.get(
        wallet=wallet,
        reference_code=expected_transaction_reference_code,
        payment_account_number=expected_transaction_payment_account_number,
    )


@pytest.mark.django_db
def test_transaction_confirmed_by_moderator(client, setup_test_data):
    """
    This test checks that when the transaction is confirmed by the moderator and that the TransactionLog, Transaction,
    and Wallet objects are updated successfully. When a moderator confirms the transaction by marking it as
    "Completed", the system updates the wallet balance when the transaction type is "Deposit" and the payment
    method is "Bank Transfer".
    """

    # required data
    user, wallet, transaction = setup_test_data

    # expected data
    wallet_before_transaction = wallet.balance
    expected_balance_after_transaction = (
        transaction.amount_paid + wallet.balance
    )
    expected_log_message = (
        "The transaction was completed successfully for the wallet with id {} and transaction with"
        " id {}".format(wallet.id, transaction.id)
    )
    # update the transaction status and payment method
    transaction.status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.COMPLETED
    )
    transaction.payment_method = PaymentMethod.objects.create(
        title=PaymentMethodConstant.BANK_TRANSFER
    )
    transaction.user = user
    transaction.save()

    # assertions
    assert wallet_before_transaction != expected_balance_after_transaction
    assert wallet.balance == expected_balance_after_transaction
    assert TransactionLog.objects.get(
        transaction=transaction, reason=expected_log_message
    )


# ------------------ Company Gifts ------------------


@pytest.mark.django_db
def test_save_company_gifts(client, setup_test_data):
    """
    This test checks that when a transaction of payment method "Gift" is created by a moderator, the TransactionLog,
     Transaction, TransactionApproval and Wallet objects are updated successfully. When a moderator creates a
        transaction of payment method "Gift", the system updates the wallet balance when the transaction type is
        "Deposit" and the payment method is "Gift".
    """

    # required data
    user, wallet, transaction = setup_test_data

    # expected data
    wallet_before_transaction = wallet.balance
    expected_balance_after_transaction = (
        transaction.amount_paid + wallet.balance
    )
    expected_log_message = (
        "The gift transaction was completed successfully for the wallet with id {} and transaction with "
        "id {}".format(wallet.id, transaction.id)
    )
    expected_reason_message = "This is a test gift"

    # update the transaction status and payment method
    transaction.status = TransactionStatus.objects.create(title="Completed")
    transaction.payment_method = PaymentMethod.objects.create(title="Gift")
    transaction.notes = expected_reason_message
    transaction.user = user
    transaction.save()

    # assertions
    assert wallet_before_transaction != expected_balance_after_transaction
    assert wallet.balance == expected_balance_after_transaction
    assert TransactionLog.objects.get(
        transaction=transaction, reason=expected_log_message
    )
    assert TransactionApproval.objects.get(
        transaction=transaction, reason=expected_reason_message
    )
