from django.urls import path
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)

from .views import (
    login,
    login_email,
    login_email_verify,
    auth_test,
    me,
    token_refresh,
)

auth_urls = [
    path("login/", login, name="login"),
    path("login/email/", login_email, name="login-email"),
    path("login/email/verify/", login_email_verify, name="login-email-verify"),
    path("test/", auth_test, name="auth-test"),
    path("me/", me, name="me"),
    path("token/refresh/", token_refresh, name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
]
