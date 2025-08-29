"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.index, name="home"),
    path("authenticate", views.authenticate_user, name="login"),
    path("create_account", views.create_account, name="create_account"),
    path("password_reset_sent", views.password_reset_sent, name="password_reset_sent_user"),
    path("password_reset/", views.ResetPasswordView.as_view(), name="reset_password_user"),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='commonui/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete_user')),
         name='password_reset_confirm_user'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='commonui/password_reset_complete.html'),
         name='password_reset_complete_user'),
    path("privacy_policy", views.privacy_policy, name="privacy_policy"),
]