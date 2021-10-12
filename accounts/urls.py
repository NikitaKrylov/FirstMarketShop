from accounts import forms
from re import template
from django.urls import reverse, reverse_lazy
from django.contrib import auth
from django.urls import path
from django.urls.conf import include
from django.contrib.auth import views as auth_views
from .forms import PasswordResetForm, SetPasswordForm
from . import views

app_name = 'accounts'

urlpatterns = [
    path('user/<slug:pk>', views.AccountDetailView.as_view(), name='user_account'),
    path('user/<slug:pk>/update/<str:field>', views.UpdateAccount.as_view(), name='update_account'),

    path('login/', views.LoginFormView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('vk-login/', include('social_django.urls'), name='vk-login'),

    path('password_reset/', auth_views.PasswordResetView.as_view(  # Форма ввода почты от аккаунта
        success_url=reverse_lazy('accounts:password_reset_done'),
        email_template_name='accounts/password_reset/password_reset_email.html',
        template_name='accounts/password_reset/password_reset_form.html',
        form_class=PasswordResetForm
    ),
        name='password_reset'),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(  # Сообщение об отправке ссылки на изменение пароля
         template_name='accounts/password_reset/password_reset_done.html'),
         name='password_reset_done'),

    path('password_reset/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(  # Форма для воода нового пароля
        success_url=reverse_lazy('accounts:password_reset_complete'),
        template_name='accounts/password_reset/password_reset_confirm.html',
        form_class=SetPasswordForm
    ),
        name='password_reset_confirm'),

    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
         template_name='accounts/password_reset/password_reset_complete.html'),
         name='password_reset_complete')
]
