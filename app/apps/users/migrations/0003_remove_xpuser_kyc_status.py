# Generated by Django 4.2.8 on 2024-01-16 17:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_xpuser_kyc_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="xpuser",
            name="kyc_status",
        ),
    ]