from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("manage_details/", views.details, name="details"),
]