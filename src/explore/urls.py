"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="explore"),
    path("search", views.search, name="search"),
    path("search/tag/<str:tag>", views.getTagResult, name="search"),
]