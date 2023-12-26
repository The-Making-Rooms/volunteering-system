from django.urls import path

from . import views

urlpatterns = [
    path("<int:opportunity_id>/", views.detail, name="detail"),
]