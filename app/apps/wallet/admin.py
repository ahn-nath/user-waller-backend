from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import (
    Wallet,
    Currency,
    Transaction,
    TransactionType,
    TransactionStatus,
    PaymentMethod,
    PaymentProvider,
    TransactionLog,
    TransactionApproval,
)


class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "currency", "balance", "view_students_link")

    def view_students_link(self, obj):
        url = (
                reverse("wallet_custom_button", kwargs={"wallet_id": obj.id})
        )
        return format_html('<a href="{}">Audit</a>', url)

    view_students_link.short_description = "Audit wallet"


class TransactionAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # attach request.user to the object prior to saving.
        # docs:https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_model
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Currency)
admin.site.register(TransactionType)
admin.site.register(TransactionStatus)
admin.site.register(PaymentMethod)
admin.site.register(PaymentProvider)
admin.site.register(TransactionLog)
admin.site.register(TransactionApproval)
