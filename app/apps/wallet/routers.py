from rest_framework import routers

from .views import WalletViewSet


wallet_router = routers.DefaultRouter()
wallet_router.register(r"wallets", WalletViewSet)


wallet_urls = wallet_router.urls
