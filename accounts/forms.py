from django import forms
from django.contrib.auth.forms import PasswordResetForm as DefaultPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as DefaultSetPasswordForm
from django.contrib.auth import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.http import request

from accounts.models import Account


class LogInAccount(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'login-input', 'placeholder': 'Имя пользователя или почта'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'login-input', 'placeholder': 'Пароль'}))

    def castome_authenticate(self, login=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=login)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    def clean(self):
        login = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not User.objects.filter(Q(username=login) | Q(email=login)):
            return self.add_error('username', ValidationError('Такого пользователя не существует!'))

        self.user_cache = self.castome_authenticate(login, password)

        if self.user_cache is None:
            self.user_cache = authenticate(
                self.request, username=login, password=password)

            if self.user_cache is None:
                return self.add_error('password', ValidationError('Неверный пароль!'))

        self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegisterAccount(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'login-input', 'placeholder': 'Имя пользователя'}))
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'class': 'login-input', 'placeholder': 'Почта'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'login-input', 'placeholder': 'Пороль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'login-input', 'placeholder': 'Повтор пороля'}))

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email):
            raise ValidationError(
                'Пользователь с такой почтой уже существует.')
        else:
            return email


class PasswordResetForm(DefaultPasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={'autocomplete': 'email', 'class': 'login-input', 'placeholder': 'Почта'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except:
            raise ValidationError('Пользователя с такой почтой не существует!')
        else:
            return email


class SetPasswordForm(DefaultSetPasswordForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'login-input', 'placeholder': 'Новый пароль'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'login-input', 'placeholder': 'Подтверждение пароля'}),
    )

