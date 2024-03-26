from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:chat_id>/", views.get_chat_content, name="chat"),
    path("<int:chat_id>/send/", views.send_message, name="send_message"),
]