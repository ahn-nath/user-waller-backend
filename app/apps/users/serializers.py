from rest_framework import serializers

from .models import XPUser


class XPUserSerializer(serializers.ModelSerializer):
    kyc_status = serializers.ReadOnlyField()

    class Meta:
        model = XPUser
        fields = "__all__"
