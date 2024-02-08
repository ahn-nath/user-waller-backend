import random

from rest_framework import status


random_number = random.randrange(0, 99999, 1)


login_credentials_headers = ", ".join(
    [
        "username",
        "status_code",
    ]
)

login_credentials_data = [
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
    ),
    (
        f"user_{random.randrange(0, 9999, 1)}@server.com",
        status.HTTP_200_OK,
    ),
    (
        "user_server.com",
        status.HTTP_400_BAD_REQUEST,
    ),
]
