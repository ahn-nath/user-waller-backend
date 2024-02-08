# Pytest
import pytest

from django.contrib.auth import get_user_model
from apps.wallet.models import (
    Wallet,
    Currency,
    PaymentMethod,
    PaymentProvider,
    TransactionStatus,
    TransactionType,
    Transaction,
    TransactionLog,
)

from app.apps.wallet.constants import (
    TransactionStatusConstant,
    TransactionTypeConstant,
    PaymentMethodConstant,
    PaymentProviderConstant,
)


@pytest.mark.django_db
def test_create_wallet_instance():
    """
    Assert that after creating and saving a Wallet object, it will exist in the test database
    """
    # create a user and a currency object
    currency = Currency.objects.create(title="USD", symbol="$")
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email="normal@user.com", password="foo"
    )
    # create a wallet object
    wallet_object = Wallet.objects.create(
        user_id=user.id,
        balance=0,
        currency=currency,
    )
    wallet_object.save()

    # assert that the object exists in the database
    assert Wallet.objects.get(user_id=user.id, balance=0, currency=currency)


@pytest.mark.django_db
def test_create_payment_method_instance():
    """
    Assert that after creating and saving a PaymentMethod object, it will exist in the test database
    """

    payment_method_object = PaymentMethod.objects.create(
        title=PaymentMethodConstant.CARD
    )
    payment_method_object.save()

    assert PaymentMethod.objects.get(title=PaymentMethodConstant.CARD)


@pytest.mark.django_db
def test_create_payment_provider_instance():
    """
    Assert that after creating and saving a PaymentMethod object, it will exist in the test database
    """

    payment_provider_object = PaymentProvider.objects.create(
        title=PaymentProviderConstant.PAYPAL
    )
    payment_provider_object.save()

    assert PaymentProvider.objects.get(title=PaymentProviderConstant.PAYPAL)


@pytest.mark.django_db
def test_create_transaction_status_instance():
    """
    Assert that after creating and saving a TransactionStatus object, it will exist in the test database
    """

    transaction_status_object = TransactionStatus.objects.create(
        title=TransactionStatusConstant.PENDING
    )
    transaction_status_object.save()

    assert TransactionStatus.objects.get(
        title=TransactionStatusConstant.PENDING
    )


@pytest.mark.django_db
def test_create_transaction_type_instance():
    """
    Assert that after creating and saving a TransactionType object, it will exist in the test database
    """

    transaction_type_object = TransactionType.objects.create(
        title=TransactionTypeConstant.DEPOSIT
    )
    transaction_type_object.save()

    assert TransactionType.objects.get(title=TransactionTypeConstant.DEPOSIT)


@pytest.mark.django_db
def test_create_currency_instance():
    """
    Assert that after creating and saving a Currency object, it will exist in the test database
    """
    currency_object = Currency.objects.create(
        title="USD",
        symbol="$",
    )
    currency_object.save()

    # assert that the object exists in the database
    assert Currency.objects.get(title="USD")
    assert Currency.objects.get(title="USD").symbol == "$"


@pytest.mark.django_db
def test_create_transaction_instance():
    """
    Assert that after creating and saving a Transaction object, it will exist in the test database
    """

    # create required objects
    get_user_model()
    user = get_user_model().objects.create_user(
        email="test.user@gmail.com", password="foo"
    )
    currency = Currency.objects.create(title="USD", symbol="$")
    status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.PENDING
    )
    type = TransactionType.objects.create(title=TransactionTypeConstant.DEPOSIT)
    payment_method = PaymentMethod.objects.create(
        title=PaymentMethodConstant.CARD
    )
    payment_provider = PaymentProvider.objects.create(
        title=PaymentProviderConstant.PAYPAL
    )
    wallet = Wallet.objects.create(
        user_id=user.id,
        balance=0,
        currency=currency,
    )
    # create a transaction object
    transaction_object = Transaction.objects.create(
        wallet=wallet,
        amount_paid=100.12,
        currency=currency,
        status=status,
        type=type,
        payment_method=payment_method,
        payment_provider=payment_provider,
    )

    transaction_object.save()

    # assert that the object exists in the database
    assert Transaction.objects.get(
        wallet=wallet,
        currency=currency,
        status=status,
        type=type,
        payment_method=payment_method,
        payment_provider=payment_provider,
    )


@pytest.mark.django_db
def test_create_transaction_log_instance():
    """
    Assert that after creating and saving a TransactionLog object, it will exist in the test database
    """

    # create required objects
    # create required objects
    get_user_model()
    user = get_user_model().objects.create_user(
        email="test.user@gmail.com", password="foo"
    )
    currency = Currency.objects.create(title="USD", symbol="$")
    previous_status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.PENDING
    )
    new_status = TransactionStatus.objects.create(
        title=TransactionStatusConstant.COMPLETED
    )
    type = TransactionType.objects.create(title=TransactionTypeConstant.DEPOSIT)
    payment_method = PaymentMethod.objects.create(
        title=PaymentMethodConstant.CARD
    )
    payment_provider = PaymentProvider.objects.create(
        title=PaymentProviderConstant.PAYPAL
    )
    wallet = Wallet.objects.create(
        user_id=user.id,
        balance=0,
        currency=currency,
    )
    # create a transaction object
    transaction_object = Transaction.objects.create(
        wallet=wallet,
        amount_paid=100.12,
        currency=currency,
        status=new_status,
        type=type,
        payment_method=payment_method,
        payment_provider=payment_provider,
    )

    # create a transaction log object
    transaction_log_object = TransactionLog.objects.create(
        transaction=transaction_object,
        prev_status=previous_status,
        new_status=new_status,
        changed_by="user test",
        reason="test reason",
    )
    transaction_log_object.save()

    # assert that the object exists in the database
    assert TransactionLog.objects.get(
        transaction=transaction_object,
        prev_status=previous_status,
        new_status=new_status,
        changed_by="user test",
        reason="test reason",
    )
