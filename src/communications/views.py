from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Chat, Message, MessageSeen, AutomatedMessage
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from django.conf import settings
from better_profanity import profanity
from org_admin.models import OrganisationAdmin
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from opportunities.models import Registration
from volunteer.models import Volunteer
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            print("user is superuser")
            return HttpResponseRedirect("/org_admin")
        elif OrganisationAdmin.objects.filter(user=request.user).exists():
            return HttpResponseRedirect("/org_admin")
    
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


def get_chat_content(request, chat_id, error=None):
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
            "error": error,
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
        if chat.organisation:
            if OrganisationAdmin.objects.filter(user=user, organisation=chat.organisation).exists():
                chat.participants.add(user)
            else:
                return HTTPResponseHXRedirect("/communications")
        else:
            return HTTPResponseHXRedirect("/communications")

    message = request.POST["message"]
    
    if profanity.contains_profanity(message):
        return get_chat_content(request, chat_id, error="Profanity is not allowed")
    
    sent_message = Message.objects.create(chat=chat, sender=user, content=message)
    
    
    if chat.chip_in_admins_chat:
        payload = {
            "head": "Chip In",
            "body": message,
            "url": "/communications/" + str(chat_id) + "/",
            "icon": settings.STATIC_URL + "images/icons/icon-512x512.png"
        }
        #superusers = User.objects.filter(is_superuser=True)
        #for superuser in superusers:
            #if superuser != request.user:
                #send_user_notification(user=superuser, payload=payload, ttl=1000)
                
                
                #send_mail(
                #    'Chip In - New Message from {} {} ({})'.format(request.user.first_name, request.user.last_name, request.user.email),
                #    """
                #    You have a new message from {} {} ({}) in the chat with {}.
                #    Please log onto the Chip In app to view the message.
                #    
                #    """.format(request.user.first_name, request.user.last_name, request.user.email, org_name),
                #    from_email=None,
                #    recipient_list=[superuser.email],
                #    fail_silently=True,
                #)
    else:
        org_name = chat.organisation.name
        payload = {
            "head": org_name,
            "body": message,
            "url": "/communications/" + str(chat_id) + "/",
            "icon": settings.STATIC_URL + "images/icons/icon-512x512.png"
        }
    
        #for user in chat.participants.all():
            #if user != request.user:
                #send_user_notification(user=user, payload=payload, ttl=1000)
                
                #send_mail(
                #    'Chip In - New Message from {} {} ({})'.format(request.user.first_name, request.user.last_name, request.user.email),
                #    """
                #    You have a new message from {} {} ({}) in the chat with {}.
                #    Please log onto the Chip In app to view the message.
                #    
                #    """.format(request.user.first_name, request.user.last_name, request.user.email, org_name),
                #    from_email=None,
                #    recipient_list=[user.email],
                #    fail_silently=True,
                #)
                    
    #Send an automated message
    
    
        automated_message = AutomatedMessage.objects.get(organisation=chat.organisation) if AutomatedMessage.objects.filter(organisation=chat.organisation).exists() else None
    
        if not automated_message:
            print("No automated message")
            return get_chat_content(request, chat_id)
        else:
            #check if an automoted message exists in the chat on the day the mesage was sent
            automated_chat_message = Message.objects.filter(chat=chat, timestamp__date=sent_message.timestamp.date(), content=automated_message.content).exists()
            
            if automated_chat_message:
                print("Automated message already exists")
                return get_chat_content(request, chat_id)
            
            message = automated_message.content
            #get superuser:
            try:
                superuser = User.objects.filter(is_superuser=True)
                Message.objects.create(chat=chat, sender=superuser[0], content=message, automated=True)
                return get_chat_content(request, chat_id)
            except Exception as e:
                print(e)

    return get_chat_content(request, chat_id)
