"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:chat_id>/", views.get_chat_content, name="chat"),
    path("<int:chat_id>/send/", views.send_message, name="send_message"),
    path("mark_seen/<int:message_id>/", views.mark_as_seen, name="mark_as_seen"),
]