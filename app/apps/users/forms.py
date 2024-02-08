from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import XPUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = XPUser
        fields = ("email", "age", "gender")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = XPUser
        fields = ("email", "age", "gender")
