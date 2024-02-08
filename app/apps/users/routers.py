from rest_framework import routers

from .viewsets import XPUserViewSet


users_router = routers.DefaultRouter()
users_router.register(r"users", XPUserViewSet)


users_urls = users_router.urls
