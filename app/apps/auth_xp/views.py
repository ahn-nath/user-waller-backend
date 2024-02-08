import logging

from sesame.utils import get_query_string, get_user
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.auth_xp.email import send_email
from apps.auth_xp.serializers import (
    LoginSerializer,
    LoginTokenSerializer,
    LoginMagicLinkSerializer,
)
from apps.users.serializers import XPUserSerializer


@swagger_auto_schema(method="post", tags=["auth"], request_body=LoginSerializer)
@api_view(["POST"])
def login(request):
    """
    Takes an email and returns a refresh type JSON web token, and a user object.
    """

    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get("email")
    user, created = get_user_model().objects.get_or_create(email=email)
    refresh = RefreshToken.for_user(user)
    token = {
        settings.COOKIE_NAME_REFRESH_TOKEN: str(refresh),
        settings.COOKIE_NAME_ACCESS_TOKEN: str(refresh.access_token),
        "user": XPUserSerializer(user).data,
    }
    response = Response(data=token)
    response.set_cookie(
        settings.COOKIE_NAME_ACCESS_TOKEN,
        token[settings.COOKIE_NAME_ACCESS_TOKEN],
        httponly=True,
    )
    response.set_cookie(
        settings.COOKIE_NAME_REFRESH_TOKEN,
        token[settings.COOKIE_NAME_REFRESH_TOKEN],
        httponly=True,
    )
    return response


@swagger_auto_schema(method="get", tags=["auth"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auth_test(request):
    """
    Test endpoint for authentication.
    """
    return Response(data={"message": "ok"})


@swagger_auto_schema(method="get", tags=["auth"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Returns the currently authenticated user.
    """

    # due to a NextAuth/NextJS limitation, we return a refreshed access token
    # yes the code with login_email_verify seems duplicated, we keep it due to req

    refresh_token = RefreshToken.for_user(request.user)
    jwt_token_with_user = {
        settings.COOKIE_NAME_REFRESH_TOKEN: str(refresh_token),
        settings.COOKIE_NAME_ACCESS_TOKEN: str(refresh_token.access_token),
        "user": XPUserSerializer(request.user).data,
    }

    return Response(data=jwt_token_with_user)


@swagger_auto_schema(
    method="post", tags=["token"], request_body=TokenRefreshSerializer
)
@api_view(["POST"])
def token_refresh(request):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer = TokenRefreshSerializer(data=request.data)
    try:
        if serializer.is_valid():
            access = serializer.validated_data.get("access")
        else:
            return Response(serializer.errors, status=400)
    except Exception as e:
        logging.error(f"token_refresh error: {e}")
        return Response({"error": str(e)}, status=400)

    # Decode the refresh token to get the user ID
    try:
        untyped_token = UntypedToken(access)
        user_id = untyped_token[settings.SIMPLE_JWT["USER_ID_CLAIM"]]
    except TokenError as e:
        raise InvalidToken(e.args[0])

    # Extract the user from the existing refresh token
    user = get_user_model().objects.get(id=user_id)

    # Generate a new refresh token for the user
    refresh_token = RefreshToken.for_user(user)
    token = {
        settings.COOKIE_NAME_REFRESH_TOKEN: str(refresh_token),
        settings.COOKIE_NAME_ACCESS_TOKEN: str(refresh_token.access_token),
    }

    response = Response(data=token)
    response.set_cookie(
        settings.COOKIE_NAME_ACCESS_TOKEN, token["access_token"], httponly=True
    )
    response.set_cookie(
        settings.COOKIE_NAME_REFRESH_TOKEN,
        token["refresh_token"],
        httponly=True,
    )
    return response


@swagger_auto_schema(
    method="post", tags=["auth"], request_body=LoginMagicLinkSerializer
)
@api_view(["POST"])
def login_email(request):
    """
    Takes an email and sends a magic link to the user.
    """

    serializer = LoginMagicLinkSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get("email")
        callback_url = serializer.validated_data.get("callback_url")
    else:
        return Response(serializer.errors, status=400)

    user, created = get_user_model().objects.get_or_create(email=email)

    querystring = get_query_string(user)
    login_url = f"{callback_url}access/email-verification{querystring}"
    send_email(
        user.email,
        "Login to your account",
        f"Click here to login: {login_url}",
    )

    return Response(data={"login_url": login_url})


@swagger_auto_schema(
    method="post", tags=["auth"], request_body=LoginTokenSerializer
)
@api_view(["POST"])
def login_email_verify(request):
    """
    Takes a login link token and returns a refresh type JSON web token, and a user object.
    """
    serializer = LoginTokenSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data.get("token")
    else:
        return Response(serializer.errors, status=400)

    user = get_user(token)
    if not user:
        return Response(status=400)

    refresh_token = RefreshToken.for_user(user)
    jwt_token_with_user = {
        settings.COOKIE_NAME_REFRESH_TOKEN: str(refresh_token),
        settings.COOKIE_NAME_ACCESS_TOKEN: str(refresh_token.access_token),
        "user": XPUserSerializer(user).data,
    }

    return Response(data=jwt_token_with_user)
