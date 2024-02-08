import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import XPUserManager


class XPUser(AbstractUser):
    class Gender(models.TextChoices):
        MAN = "00"
        WOMAN = "01"
        HE_TRANS = "02"
        SHE_TRANS = "03"
        COUPLE_MW = "04"
        COUPLE_WW = "05"
        COUPLE_MM = "06"
        COUPLE_TW = "07"
        NONE = "08"

    username = None
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=2,
        choices=Gender.choices,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = XPUserManager()

    def __str__(self):
        return self.email

    @property
    def kyc_status(self):
        last_kyc_attempt = self.kycattempt_set.last()
        if last_kyc_attempt:
            return last_kyc_attempt.status_label
        else:
            return self.kycattempt_set.model.Status.INVALID.label
