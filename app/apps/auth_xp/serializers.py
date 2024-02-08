from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class LoginMagicLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    callback_url = serializers.CharField(required=True)


class LoginTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
