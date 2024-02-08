from django.urls import path

from . import views

urlpatterns = [
    path("<int:opportunity_id>/", views.detail, name="detail"),
    path("<int:opportunity_id>/register/", views.register, name="register"),
]