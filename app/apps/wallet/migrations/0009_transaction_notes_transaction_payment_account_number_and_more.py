# Generated by Django 4.2.8 on 2024-01-17 21:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "wallet",
            "0008_alter_currency_title_alter_paymentmethod_title_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="notes",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="transaction",
            name="payment_account_number",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="transaction",
            name="reference_code",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
