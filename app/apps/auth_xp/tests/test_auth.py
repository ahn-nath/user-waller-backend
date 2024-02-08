import pytest

from rest_framework.test import APIClient

from app.tests.utils_test import BASE_URL
from .test_input_cases import login_credentials_headers, login_credentials_data


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.authxp
@pytest.mark.django_db
@pytest.mark.parametrize(
    login_credentials_headers,
    login_credentials_data,
)
def test_login(
    api_client,
    username,
    status_code,
):
    login_url = BASE_URL + "auth/login/"
    login_input_data = {
        "email": username,
    }
    login_response = api_client.post(
        login_url,
        login_input_data,
        format="json",
    )
    assert login_response.status_code == status_code
