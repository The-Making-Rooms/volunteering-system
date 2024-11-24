from communications.models import Chat, Message, MessageSeen
from ..models import OrganisationAdmin
from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from better_profanity import profanity
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.models import User

def get_org_chats(request, preload_chat_id=None):
    if not request.user.is_superuser:
        org = OrganisationAdmin.objects.get(user=request.user).organisation
        chats = Chat.objects.filter(organisation=org)
    elif request.user.is_superuser:
        chats = Chat.objects.all()
        
    chat_admins = OrganisationAdmin.objects.filter().values_list("user", flat=True)
    superusers = OrganisationAdmin.objects.filter(user__is_superuser=True).values_list("user", flat=True)
        
    print(chats)
    chat_objs = []
    
    for chat in chats:
        non_org_participants = chat.participants.exclude(id__in=chat_admins)
        non_org_participants = non_org_participants.exclude(id__in=superusers)
        has_messages = Message.objects.filter(chat=chat).exists()
        if not has_messages:
            continue
        latest_message = Message.objects.filter(chat=chat).order_by("-timestamp").first()
        if latest_message:
            latest_read_by_org_admin = MessageSeen.objects.filter(message=latest_message, user__in=chat_admins).exists() if chat.organisation else MessageSeen.objects.filter(message=latest_message, user__in=superusers).exists()
        chat_obj = {
            "id": chat.id,
            "participants": non_org_participants,
            "organisation": "Chip In" if chat.chip_in_admins_chat else chat.organisation.name,
            "broadcast": chat.broadcast,
            "latest_read_by_org_admin": latest_read_by_org_admin,
        }
        
        chat_objs.append(chat_obj)
        
    #print(chat_objs)
    
    context = {
        "chats": chat_objs,
        "user": request.user,
        "admin": chat_admins,
        "preload_chat_id": preload_chat_id,
        "hx": check_if_hx(request),
    }
    return render(request, "org_admin/chats.html", context)

def get_chat_content(request, chat_id, error=None):
    if request.method == "POST":
        return send_message(request, chat_id)
    user = request.user
    chat = Chat.objects.get(id=chat_id)
    
    try:
        org = OrganisationAdmin.objects.get(user=user).organisation
    except OrganisationAdmin.DoesNotExist:
        org = None
        
    if not user.is_superuser and not org:
        return HTTPResponseHXRedirect("/org_admin/communications")

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
    
     
    if not user.is_superuser: org = OrganisationAdmin.objects.get(user=user).organisation

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
    
    #check if its the first sent
    existing_messages = Message.objects.filter(chat=chat).count()

    Message.objects.create(chat=chat, sender=user, content=message)
    
    if existing_messages == 0:
        chat_notification(chat_id)
    


    request.method = "GET"
    return get_chat_content(request, chat_id)


def chat_notification(chat_id):
    chat = Chat.objects.get(id=chat_id)
    

    
    exclude_list = []
    send_list = []
    
    superusers = User.objects.filter(is_superuser=True)
    exclude_list.extend(superusers)
    
    if chat.organisation:
        org_admins = OrganisationAdmin.objects.filter(organisation=chat.organisation)
        print(org_admins)
        admins_users = [admin.user for admin in org_admins]
        exclude_list.extend(admins_users)
        
    for participant in chat.participants.all():
        if participant not in exclude_list:
            send_list.append(participant)
            
            
    print(exclude_list)
    print(send_list)
    
    from_string = "Chip in Team" if not chat.organisation else chat.organisation.name
    
    email = """
Hi,

You have a new chat from """ + from_string + """ on Chip In. Please log in to view it.

Thanks,
Chip In"""


    send_mail(
        "Chip In: New message from " + from_string,
        email,
        fail_silently=True,
        recipient_list=[user.email for user in send_list],
        from_email="no-reply@chipinbwd.co.uk",
    )


        #org_name = chat.organisation.name
    #payload = {
    #    "head": org_name,
    #    "body": message,
    #    "url": "/communications/" + str(chat_id) + "/",
    #}

    #for user in chat.participants.all():
    #    if user != request.user:
    #        send_user_notification(user=user, payload=payload, ttl=1000)
    
    
        
    
    