from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
import logging

# initialize logger
from .constants import (
    TransactionTypeConstant,
    PaymentMethodConstant,
    TransactionStatusConstant,
)

logger = logging.getLogger(__name__)


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    currency = models.ForeignKey("Currency", on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.currency} - {self.balance}"


class Currency(models.Model):
    title = models.CharField(max_length=200, unique=True)
    symbol = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.title


class Transaction(models.Model):
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    type = models.ForeignKey("TransactionType", on_delete=models.CASCADE)
    status = models.ForeignKey("TransactionStatus", on_delete=models.CASCADE)
    payment_method = models.ForeignKey(
        "PaymentMethod", on_delete=models.CASCADE
    )
    payment_provider = models.ForeignKey(
        "PaymentProvider", on_delete=models.CASCADE
    )
    currency = models.ForeignKey("Currency", on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_account_number = models.CharField(
        max_length=200, null=True
    )  # for bank transactions and card transactions
    reference_code = models.CharField(max_length=200, null=True)
    notes = models.TextField(
        null=True
    )  # it can contain additional information about the transaction, like bank name

    def save(self, *args, **kwargs):
        """
        This method is used to save the transaction object. It updates the wallet balance when the transaction is
        "Deposit", the payment method is "Bank Transfer", and the transaction status is "Completed".

        docs: https://docs.djangoproject.com/en/5.0/topics/db/models/#overriding-predefined-model-methods

        """

        # Get the current user from the request
        if (
            self.status.title == TransactionStatusConstant.COMPLETED
            and self.payment_method.title
            in (PaymentMethodConstant.BANK_TRANSFER, PaymentMethodConstant.GIFT)
        ):
            # if the user is not staff, throw an error
            if not hasattr(self, "user") or not self.user.is_staff:
                raise PermissionDenied(
                    "You are not authorized to perform this action."
                )

            # if "Deposit" and "Bank Transfer", update the wallet balance with the amount paid
            if (
                self.type.title == TransactionTypeConstant.DEPOSIT
                and self.payment_method.title
                == PaymentMethodConstant.BANK_TRANSFER
            ):
                self.wallet.balance += self.amount_paid
                self.wallet.save()
                super().save(*args, **kwargs)  # Call the "real" save() method.
                # create a TransactionLog object
                log_message = (
                    "The transaction was completed successfully for the wallet with id {} and transaction with "
                    "id {}".format(self.wallet.id, self.id)
                )
                TransactionLog.objects.create(
                    transaction=self,
                    reason=log_message,
                    new_status=self.status,
                )
                logger.info(log_message)

            # if "Gift", update the wallet balance, create a TransactionLog and a TransactionApproval object
            elif self.payment_method.title == PaymentMethodConstant.GIFT:
                self.wallet.balance += self.amount_paid
                self.wallet.save()
                super().save(*args, **kwargs)  # Call the "real" save() method.

                # create a TransactionApproval object
                TransactionApproval.objects.create(
                    transaction=self,
                    moderator=self.user,
                    reason=self.notes,
                )

                # create a TransactionLog object
                log_message = (
                    "The gift transaction was completed successfully for the wallet with id {} and transaction with "
                    "id {}".format(self.wallet.id, self.id)
                )

                TransactionLog.objects.create(
                    transaction=self,
                    reason=log_message,
                    new_status=self.status,
                )
                logger.info(log_message)

        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return f"{self.pk} - {self.created_at} - {self.amount_paid}"


class TransactionType(models.Model):
    title = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TransactionStatus(models.Model):
    title = models.CharField(max_length=200, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Transaction statuses"

    def __str__(self):
        return self.title


class TransactionLog(models.Model):
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE)
    prev_status = models.ForeignKey(
        "TransactionStatus",
        on_delete=models.CASCADE,
        related_name="prev_status",
        null=True,  # the first log will have a null prev_status
    )
    new_status = models.ForeignKey(
        "TransactionStatus", on_delete=models.CASCADE, related_name="new_status"
    )
    changed_by = models.CharField(max_length=200)
    reason = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} - {self.created_at} - {self.transaction} - {self.prev_status} - {self.new_status}"


class TransactionApproval(models.Model):
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE)
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.created_at} - {self.transaction} - {self.moderator}"


class PaymentMethod(models.Model):
    title = models.CharField(max_length=200, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PaymentProvider(models.Model):
    title = models.CharField(max_length=200, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BankTransferDetails(models.Model):
    bank_name = models.CharField(max_length=200)
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)
    CBU = models.CharField(max_length=200)
    branch = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.alias}"
