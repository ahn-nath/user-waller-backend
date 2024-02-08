from rest_framework import serializers

# from .models import Wallet
from apps.wallet.models import Wallet, BankTransferDetails


class WalletSerializer(serializers.ModelSerializer):
    """
    Wallet serializer
    """

    class Meta:
        model = Wallet
        fields = "__all__"


class BankTransferDetailsSerializer(serializers.ModelSerializer):
    """
    Bank Transfer Details serializer
    """

    class Meta:
        model = BankTransferDetails
        fields = "__all__"


# noqa is being used because it is a known bug in Pycharm: https://youtrack.jetbrains.com/issue/PY-16776
class BankTransactionSerializer(
    serializers.Serializer
):  # noqa: Class must implement all abstract methods.

    """
    This serializer is used to validate the data sent to the API endpoint for bank transactions.
    """

    amount_paid = serializers.FloatField()
    payment_account_number = serializers.CharField(
        max_length=200, required=False
    )
    reference_code = serializers.CharField(max_length=200, required=False)
    transaction_date = serializers.DateTimeField()
    sender_recipient_info = serializers.CharField(
        max_length=200, required=False
    )
    transaction_description = serializers.CharField(
        max_length=200, required=False
    )
    bank_name = serializers.CharField()
