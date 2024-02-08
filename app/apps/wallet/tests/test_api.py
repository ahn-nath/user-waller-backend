import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from apps.wallet.models import Wallet, Currency


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
    user_admin = user_model.objects.create_user(
        email="admin@user.com",
        password="foo",
        is_staff=True,
        first_name="Admin",
        last_name="User",
    )
    currency = Currency.objects.create(title="USD", symbol="$")
    wallet = Wallet.objects.create(
        user_id=user.id, balance=2000, currency=currency
    )

    return user, user_admin, currency, wallet


@pytest.mark.django_db
def test_wallet_endpoint_by_id_returns_balance(client, setup_test_data):
    """
    Assert that the Wallet endpoint by Wallet ID returns the balance of the wallet when it has the
    correct permissions.

    endpoint: wallets/wallet/<wallet_id>
    """
    # required data
    user, user_admin, currency, wallet = setup_test_data

    # authenticate admin user
    client.post(
        "/auth/login/",
        {"email": user_admin.email, "password": "foo"},
        format="json",
    )

    # make request
    url = reverse(
        "wallet-get-balance-by-wallet-id", kwargs={"wallet_id": wallet.id}
    )
    response = client.get(url, format="json", wallet_id=wallet.id)

    # assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.data == wallet.balance


@pytest.mark.django_db
def test_wallet_endpoint_by_id_fails(client, setup_test_data):
    """
    Assert that the Wallet endpoint by Wallet ID fails when it has incorrect permissions.

    endpoint: wallet/wallet/<wallet_id>
    """
    # required data
    (
        _,
        _,
        _,
        wallet,
    ) = setup_test_data  # Destructuring values from setup_test_data

    # make request
    url = reverse("wallet-get-balance-by-wallet-id", kwargs={"wallet_id": 1})
    response = client.get(url, format="json", wallet_id=wallet.id)

    # assertions
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_wallet_endpoint_by_user_id_returns_balance(client, setup_test_data):
    """
    Assert that the Wallet endpoint by User ID returns the balance of the wallet when it has the
    correct permissions.

    endpoint: wallets/wallet/<user_id>
    """
    # required data
    (
        _,
        user_admin,
        _,
        wallet,
    ) = setup_test_data  # Destructuring values from setup_test_data

    # authenticate admin user
    client.post(
        "/auth/login/",
        {"email": user_admin.email, "password": "foo"},
        format="json",
    )

    # make request
    url = reverse(
        "wallet-get-balance-by-user-id", kwargs={"user_id": wallet.user_id}
    )
    response = client.get(url, format="json", user_id=wallet.user_id)

    # assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.data == wallet.balance


@pytest.mark.django_db
def test_wallet_endpoint_by_user_id_fails(client, setup_test_data):
    """
    Assert that the Wallet endpoint by User ID fails when it has incorrect permissions.

    endpoint: wallet/wallet/<user_id>
    """
    (
        _,
        _,
        _,
        wallet,
    ) = setup_test_data  # Destructuring values from setup_test_data

    # make request
    url = reverse(
        "wallet-get-balance-by-user-id",
        kwargs={"user_id": "c7883a23-b67c-4f34-a58d-4f7571ca768e"},
    )
    response = client.get(url, format="json", user_id=wallet.user_id)

    # assertions
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_wallet_endpoint_by_authenticated_user_returns_wallet(
    client, setup_test_data
):
    """
    Assert that the Wallet endpoint by authenticated User returns the wallet when it has the
    correct permissions.

    endpoint: wallets/wallet
    """
    (
        _,
        user,
        currency,
        _,
    ) = setup_test_data  # Destructuring values from setup_test_data

    # authenticate user
    client.post(
        "/auth/login/", {"email": user.email, "password": "foo"}, format="json"
    )

    # create wallet for user
    wallet = Wallet.objects.create(
        user_id=user.id, balance=2000, currency=currency
    )
    wallet.save()

    # make request
    url = reverse("wallet-get-wallet-by-user-id")
    response = client.get(url, format="json")

    # assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == wallet.id
    assert response.data.get("balance") == "{:.2f}".format(wallet.balance)


@pytest.mark.django_db
def test_wallet_endpoint_by_authenticated_user_404(client, setup_test_data):
    """
    Assert that the Wallet endpoint by authenticated User returns 404 when it does not have an associated wallet
    object.

    endpoint: wallet/wallet
    """
    (
        _,
        user_admin,
        _,
        _,
    ) = setup_test_data  # Destructuring values from setup_test_data

    # authenticate admin user
    client.post(
        "/auth/login/",
        {"email": user_admin.email, "password": "foo"},
        format="json",
    )

    # make request
    url = reverse("wallet-get-wallet-by-user-id")
    response = client.get(url, format="json")

    # assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
