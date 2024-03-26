from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.index, name="home"),
    path("authenticate", views.authenticate_user, name="login"),
    path("create_account", views.create_account, name="create_account"),
    path("password_reset_sent", views.password_reset_sent, name="password_reset_sent"),
    path("password_reset/", views.ResetPasswordView.as_view(), name="reset_password"),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='commonui/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='commonui/password_reset_complete.html'),
         name='password_reset_complete'),
]