from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    last_name = forms.CharField(label="Фамилия", required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="Роль")
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "last_name", "email", "role", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email
