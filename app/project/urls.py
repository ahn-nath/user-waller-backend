from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from apps.auth_xp.urls import auth_urls as auth_urlpatterns
from apps.users.routers import users_urls
from apps.kyc.routers import kyc_urls
from apps.wallet.routers import wallet_urls
from apps.wallet.views import custom_button_view
from project.utils import CustomOpenAPISchemaGenerator

# NTH / TODO: https://github.com/axnsan12/drf-yasg/issues/651

base_urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),  # TODO: remove?
]

schema_view_auth = get_schema_view(
    openapi.Info(
        title="Auth API",
        default_version="v1",
        description="""
            Test description

        """,
    ),
    public=True,
    patterns=auth_urlpatterns,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
)

schema_view_users = get_schema_view(
    openapi.Info(
        title="Users API",
        default_version="v1",
        description="""
            Test description

        """,
    ),
    public=True,
    patterns=users_urls,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
)

schema_view_kyc = get_schema_view(
    openapi.Info(
        title="KYC API",
        default_version="v1",
        description="""
            Test description

        """,
    ),
    public=True,
    patterns=kyc_urls,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
)

schema_view_wallet = get_schema_view(
    openapi.Info(
        title="Wallet API",
        default_version="v1",
        description="""
            Test description

        """,
    ),
    public=True,
    patterns=wallet_urls,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
)

auth_urlpatterns += [
    path(
        "",
        schema_view_auth.with_ui(
            "swagger",
            cache_timeout=0,
        ),
        name="schema-swagger-ui-auth",
    ),
]

users_urlpatterns = [
    path(
        "",
        schema_view_users.with_ui(
            "swagger",
            cache_timeout=0,
        ),
        name="schema-swagger-ui-users",
    ),
    path("", include(users_urls)),
]

kyc_urlpatterns = [
    path(
        "",
        schema_view_kyc.with_ui(
            "swagger",
            cache_timeout=0,
        ),
        name="schema-swagger-ui-kyc",
    ),
    path("", include(kyc_urls)),
]

wallet_urlpatterns = [
    path(
        "",
        schema_view_wallet.with_ui(
            "swagger",
            cache_timeout=0,
        ),
        name="schema-swagger-ui-wallet",
    ),
    path("", include(wallet_urls)),
]


urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("", include(users_urlpatterns)),
    path("users/kyc/", include(kyc_urlpatterns)),
    path("wallet/", include(wallet_urlpatterns)),
    path(
        "admin/wallet/wallet/custom_button/<int:wallet_id>",
        custom_button_view,
        name="wallet_custom_button",
    ),
] + base_urlpatterns
