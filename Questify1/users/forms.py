from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="Роль")

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "password1", "password2")
