import os
import pytest

from rest_framework.test import APIClient

from .test_input_cases import users_headers, users_data


BASE_URL = f"http://{os.getenv('DJANGO_HOST')}:18000/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.genders
@pytest.mark.django_db
@pytest.mark.parametrize(users_headers, users_data)
def test_user_genders(
    api_client,
    status_code,
):
    gender_url = BASE_URL + "users/genders/"
    gender_response = api_client.get(gender_url)
    assert gender_response.status_code == status_code
    assert "genders" in gender_response.json()
