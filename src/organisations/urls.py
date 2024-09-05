from django.urls import path

from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path("<int:organisation_id>/", views.detail, name="detail"),
    path("<int:organisation_id>/create_chat/", views.create_chat, name="create_chat"),
    path("chipin/create_chat/", views.create_chipin_chat, name="create_chat"),
]