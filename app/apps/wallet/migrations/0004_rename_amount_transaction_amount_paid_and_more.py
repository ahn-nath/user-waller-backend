# Generated by Django 4.2.8 on 2024-01-05 15:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wallet", "0003_alter_currency_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="transaction",
            old_name="amount",
            new_name="amount_paid",
        ),
        migrations.AddField(
            model_name="transaction",
            name="amount_transferred",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="transaction",
            name="service_fee",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=10
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.CharField(max_length=200)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
