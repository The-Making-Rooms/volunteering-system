"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.get_supervisor_shifts, name='supervisor_index'),
    path("<int:occurrence_id>/", views.shift_supervisor, name='supervisor_screen'),
    path("checkin/<int:shift_id>/", views.checkin_shift, name='volunteer_checkin'),

    path('logout/', views.sign_out, name='logout'),

    path("password_reset_sent", views.password_reset_sent, name="password_reset_sent_supervisor"),
    path("password_reset/", views.ResetPasswordView.as_view(), name="reset_password"),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='org_admin/password_reset_confirm.html'),
         name='password_reset_confirm_supervisor'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='org_admin/password_reset_complete.html'),
         name='password_reset_complete'),

]