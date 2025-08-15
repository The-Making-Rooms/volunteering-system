"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("<int:opportunity_id>/", views.detail, name="detail"),
    path("<int:opportunity_id>/register/", views.register, name="register"),
    path("<int:opportunity_id>/get_dates/", views.get_opportunity_dates, name="get_dates"),

]