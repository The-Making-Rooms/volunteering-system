from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Chat, Message, MessageSeen
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from django.conf import settings

# Create your views here.


def index(request):
    user = request.user
    chats = Chat.objects.filter(participants=user)
    return render(
        request,
        "communications/index.html",
        {"hx": check_if_hx(request), "chats": chats, "link_active": "communications"},
    )


def mark_as_seen(request, message_id):
    user = request.user
    message = Message.objects.get(id=message_id)
    MessageSeen.objects.create(message=message, user=user)
    return HttpResponse("ok")


def get_chat_content(request, chat_id):
    user = request.user
    chat = Chat.objects.get(id=chat_id)

    if user not in chat.participants.all():
        return HTTPResponseHXRedirect("/communications")

    messages = Message.objects.filter(chat=chat)
    for message in messages:
        message.seen = MessageSeen.objects.filter(message=message, user=user).exists()

    return render(
        request,
        "communications/chat.html",
        {
            "hx": check_if_hx(request),
            "chat": chat,
            "messages": messages,
            "user": request.user,
            "link_active": "communications",
        },
    )


def send_message(request, chat_id):
    if request.method != "POST":
        return HTTPResponseHXRedirect("/communications")

    if request.POST["message"] == "":
        return get_chat_content(request, chat_id)

    user = request.user
    chat = Chat.objects.get(id=chat_id)

    if user not in chat.participants.all():
        return HTTPResponseHXRedirect("/communications")

    message = request.POST["message"]
    Message.objects.create(chat=chat, sender=user, content=message)
    org_name = chat.organisation.name
    payload = {
        "head": org_name,
        "body": message,
        "url": "/communications/" + str(chat_id) + "/",
    }

    for user in chat.participants.all():
        if user != request.user:
            send_user_notification(user=user, payload=payload, ttl=1000)

    return get_chat_content(request, chat_id)
