"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path

from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path("<int:form_id>/", views.fill_form, name="form_detail"),
    path("<int:form_id>/submit/", views.submit_response, name="submit_response"),
    path("<int:form_id>/submit/<int:custom_respondee>/", views.submit_response, name="submit_response")
]