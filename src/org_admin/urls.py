from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("details/", views.details, name="details"),
    path("add_location/", views.location, name="add_location"),
    path("edit_location/<int:id>/", views.location, name="edit_location"),
    path("delete_location/<int:id>/", views.location, name="delete_location", kwargs={'delete': True})
]