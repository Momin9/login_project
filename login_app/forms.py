from django import forms
from .models import UserLogin

class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=255,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Email / Phone Number / Username',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        max_length=255,
        label='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
            'id': 'password-input'
        })
    )