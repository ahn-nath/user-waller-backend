import random

from rest_framework import status


login_credentials_headers = ", ".join(
    [
        "username",
        "status_code",
        "happy_path",
    ]
)

login_credentials_data = [
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
        True,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
        True,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
        True,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
        True,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
        True,
    ),
    (
        "user_server.com",
        status.HTTP_400_BAD_REQUEST,
        False,
    ),
]
