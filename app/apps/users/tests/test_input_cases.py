# import random

from rest_framework import status


# random_number = random.randrange(0, 99999, 1)


users_headers = "status_code"
# users_headers = ", ".join(
#     [
#         "username",
#         "status_code",
#     ]
# )

users_data = [
    status.HTTP_200_OK,
    # (status.HTTP_200_OK,),
]
