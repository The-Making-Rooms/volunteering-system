"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("<int:occurrence_id>/", views.shift_supervisor, name='supervisor_screen'),
    path("checkin/<int:shift_id>/", views.checkin_shift, name='volunteer_checkin'),

]