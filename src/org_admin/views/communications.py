from communications.models import Chat, Message, MessageSeen
from ..models import OrganisationAdmin
from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from better_profanity import profanity
from datetime import datetime

def get_org_chats(request):
    org = OrganisationAdmin.objects.get(user=request.user).organisation
    chat_admins = OrganisationAdmin.objects.filter(organisation=org).values_list("user", flat=True)
    chats = Chat.objects.filter(organisation=org)
    print(chats)
    chat_objs = []
    
    for chat in chats:
        non_org_participants = chat.participants.exclude(id__in=chat_admins)
        chat_obj = {
            "id": chat.id,
            "participants": non_org_participants,
            "broadcast": chat.broadcast,
        }
        
        chat_objs.append(chat_obj)
        
    print(chat_objs)
    
    context = {
        "chats": chat_objs,
        "user": request.user,
        "admin": chat_admins,
        "hx": check_if_hx(request),
    }
    return render(request, "org_admin/chats.html", context)

def get_chat_content(request, chat_id, error=None):
    if request.method == "POST":
        return send_message(request, chat_id)
    user = request.user
    chat = Chat.objects.get(id=chat_id)
    org = OrganisationAdmin.objects.get(user=user).organisation

    if user.is_superuser:
        pass
    elif org != chat.organisation:
        return HTTPResponseHXRedirect("/org_admin/communication/")

    messages = Message.objects.filter(chat=chat)
    for message in messages:
        message.seen = MessageSeen.objects.filter(message=message, user=user).exists()

    return render(
        request,
        "org_admin/chat.html",
        {
            "hx": check_if_hx(request),
            "chat": chat,
            "messages": messages,
            "user": request.user,
            "link_active": "communications",
            "error": error,
        },
    )
    
def send_message(request, chat_id):
    if request.method != "POST":
        return HTTPResponseHXRedirect("/org_admin/communications")

    if request.POST["message"] == "":
        request.method = "GET"
        return get_chat_content(request, chat_id, error="Message cannot be empty")

    user = request.user
    chat = Chat.objects.get(id=chat_id)
    org = OrganisationAdmin.objects.get(user=user).organisation

    if user.is_superuser:
        pass
    elif org != chat.organisation:
        return HTTPResponseHXRedirect("/org_admin/communication/")
    elif user not in chat.participants.all() and org == chat.organisation:
        chat.participants.add(user)


    
    message = request.POST["message"]
    
    if profanity.contains_profanity(message):
        request.method = "GET"
        return get_chat_content(request, chat_id, error="Message contains profanity")
       
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

    request.method = "GET"
    return get_chat_content(request, chat_id)