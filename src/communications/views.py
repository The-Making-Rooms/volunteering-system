"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Chat, Message, MessageSeen, AutomatedMessage
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from django.conf import settings
from better_profanity import profanity
from org_admin.models import OrganisationAdmin, NotificationPreference
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from opportunities.models import Registration
from volunteer.models import Volunteer
from threading import Thread
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
        print(message.seen)

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
    
    
    last_message = Message.objects.filter(chat=chat, automated=False).last()
    last_user_message = Message.objects.filter(chat=chat, sender=request.user).last()
    sent_message = Message.objects.create(chat=chat, sender=user, content=message)#
    
    print("Message object created")
    
    
    if chat.chip_in_admins_chat:
        payload = {
            "head": "Chip In",
            "body": message,
            "url": "/communications/" + str(chat_id) + "/",
            "icon": settings.STATIC_URL + "images/icons/icon-512x512.png"
        }
        
    else:
        org_name = chat.organisation.name
        payload = {
            "head": org_name,
            "body": message,
            "url": "/communications/" + str(chat_id) + "/",
            "icon": settings.STATIC_URL + "images/icons/icon-512x512.png"
        }
    
        print("Automated message Check")
    
        automated_message = AutomatedMessage.objects.get(organisation=chat.organisation) if AutomatedMessage.objects.filter(organisation=chat.organisation).exists() else None
    
        if not automated_message:
            print("No automated message")
        else:
            #check if an automoted message exists in the chat on the day the mesage was sent
            automated_chat_message = Message.objects.filter(chat=chat, timestamp__date=sent_message.timestamp.date(), content=automated_message.content).exists()
            
            if automated_chat_message:
                print("Automated message already exists")
            message = automated_message.content
            #get superuser:
            try:
                superuser = User.objects.filter(is_superuser=True)
                Message.objects.create(chat=chat, sender=superuser[0], content=message, automated=True)
            except Exception as e:
                print(e)
                
                
    print("Sending notification")
    try:        
        send_email = False        
                
        #Check it has been 10 minutes since the last message was sent or if another message has been sent in the chat by another user
        
        print(last_user_message)

        
        if last_message:
            if last_message.sender != request.user:
                print("Last message was not sent by the user")
                send_email = True
        
        if last_user_message:
            time_difference = sent_message.timestamp - last_user_message.timestamp
            print (time_difference, sent_message.timestamp, last_user_message.timestamp)
            print(sent_message, last_user_message)
            if time_difference.seconds < 600:
                print("Less than 10 minutes since last message")
            else:
                print("More than 10 minutes since last message")
                send_email = True
        else:
            print ("No last message")
            send_email = True
                
        if send_email:
            excluded_emails = NotificationPreference.objects.filter(email_on_message=False).values_list('user__email', flat=True)
            
            superuser_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            organisation_admin_emails = OrganisationAdmin.objects.filter(organisation=chat.organisation).values_list('user__email', flat=True)
            emails = list(superuser_emails) + list(organisation_admin_emails)
            
            print ('excluded_emails:', excluded_emails)
            
            emails = [email for email in emails if email not in excluded_emails]
            
            print ('filtered emails:', emails)
            
            for email in emails:
                print ("Sending email to: " + email)
                
                if chat.chip_in_admins_chat:
                    SendChatEmailThread("Chip In", email, message).start()
                else:
                    SendChatEmailThread(chat.organisation.name, email, message).start()

        request.method = "GET"
        return get_chat_content(request, chat_id)
    except Exception as e:
        print('Error in communications (User Side)', e)
        return get_chat_content(request, chat_id)


def send_chat_email(organisation, recipient, message):
    subject = "Chip In: New Message for " + organisation
    message = f"""
Hello,

You have a new message from a chip in user for {organisation}.
Please login to the Chip In system to view and respond to the message.

If you wish to stop receiving these emails, you can turn them off in the profile tab on the Chip In Admin.

Regards,
The Chip In Team
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
    return
    
    
class SendChatEmailThread(Thread):
    def __init__(self, organisation, recipient, message):
        Thread.__init__(self)
        self.organisation = organisation
        self.recipient = recipient
        self.message = message
        
    def run(self):
        send_chat_email(self.organisation, self.recipient, self.message)
        return