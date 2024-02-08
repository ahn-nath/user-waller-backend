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
)
from django.urls import reverse


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
    )
    currency = Currency.objects.create(title="USD", symbol="$")
    wallet = Wallet.objects.create(
        user_id=user.id, balance=2000, currency=currency
    )
    transaction_status = TransactionStatus.objects.create(title="Pending")
    payment_method = PaymentMethod.objects.create(title="All")
    payment_provider = PaymentProvider.objects.create(title="Stripe")
    transaction_type = TransactionType.objects.create(title="Deposit")

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
    transaction_status = TransactionStatus.objects.create(title="Completed")

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
        == "Completed"
    )
    assert Transaction.objects.get(wallet=wallet).status.title == "Completed"


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
    transaction_status = TransactionStatus.objects.create(title="Cancelled")

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
    assert Transaction.objects.get(wallet=wallet).status.title == "Cancelled"
