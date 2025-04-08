from communications.models import Chat, Message, MessageSeen
from ..models import OrganisationAdmin
from django.shortcuts import render
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from better_profanity import profanity
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from threading import Thread

def get_org_chats(request, preload_chat_id=None):
    
    if not request.user.is_authenticated:
        return HTTPResponseHXRedirect("/org_admin/sign_in")
    
    
    
    if not request.user.is_superuser:
        try:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
            chats = Chat.objects.filter(organisation=org)
        except OrganisationAdmin.DoesNotExist:
            return render (request, "org_admin/no_admin.html")
        
        
    elif request.user.is_superuser:
        chats = Chat.objects.all()
       
     
    chat_admins = OrganisationAdmin.objects.filter().values_list("user", flat=True)
    superusers = User.objects.filter(is_superuser=True).values_list("id", flat=True)
        
    print(chats)
    chat_objs = []
    
    for chat in chats:
        non_org_participants = chat.participants.exclude(id__in=chat_admins)
        non_org_participants = non_org_participants.exclude(id__in=superusers)
        has_messages = Message.objects.filter(chat=chat).exists()
        latest_read_by_org_admin = False
        latest_message = Message.objects.filter(chat=chat).order_by("-timestamp").first()
        if latest_message:
            if chat.organisation:
                if (len(chat_admins) > 0):
                    latest_read_by_org_admin = MessageSeen.objects.filter(message=latest_message, user__in=superusers).exists()
                else:
                    latest_read_by_org_admin = MessageSeen.objects.filter(message=latest_message, user__in=chat_admins).exists()
                    
            else:
                latest_read_by_org_admin = MessageSeen.objects.filter(message=latest_message, user__in=superusers).exists()

        chat_obj = {
            "id": chat.id,
            "participants": non_org_participants,
            "organisation": "Chip In" if chat.chip_in_admins_chat else chat.organisation.name,
            "broadcast": chat.broadcast,
            "latest_read_by_org_admin": latest_read_by_org_admin,
            "last_message": latest_message.timestamp.replace(tzinfo=None) if latest_message else None,
        }
        
        chat_objs.append(chat_obj)
        
        # Order by latest message, None at top
        chat_objs.sort(key=lambda x: x['last_message'] if x['last_message'] is not None else datetime.max, reverse=True)
        
        
        
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
    
    if not request.user.is_authenticated:
        return HTTPResponseHXRedirect("/org_admin/sign_in")
    
    
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
    chat_recipients = []
    
    non_org_participants = chat.participants.exclude(id__in=OrganisationAdmin.objects.filter().values_list("user", flat=True))
    non_org_participants = non_org_participants.exclude(id__in=User.objects.filter(is_superuser=True).values_list("id", flat=True))
    
    
    for participant in non_org_participants:
        if participant not in chat_recipients:
            chat_recipients.append(User.objects.get(id=participant.id).first_name + " " + User.objects.get(id=participant.id).last_name)

    for message in messages:
        message.seen = MessageSeen.objects.filter(message=message, user=user).exists()
        
        message_seen_by_non_org_participants = MessageSeen.objects.filter(message=message, user__in=non_org_participants).exists()
        print(message_seen_by_non_org_participants)
        message.seen_by_non_org_participants = message_seen_by_non_org_participants
        
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
            "non_org_participants": non_org_participants,
            "chat_recipients": chat_recipients,
        },
    )
    
def send_message(request, chat_id):
    
    if not request.user.is_authenticated:
        return HTTPResponseHXRedirect("/org_admin/sign_in")
    if not request.user.is_superuser:
        try:
            org = OrganisationAdmin.objects.get(user=request.user).organisation
        except OrganisationAdmin.DoesNotExist:
            return render(request, "org_admin/no_admin.html")
    
    if request.method != "POST":
        return HTTPResponseHXRedirect("/org_admin/communications")

    if request.POST["message"] == "":
        request.method = "GET"
        return get_chat_content(request, chat_id, error="Message cannot be empty")
    
    
    
    user = request.user
    chat = Chat.objects.get(id=chat_id)
    
     
    if not user.is_superuser: 
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
    
    #check if its the first sent
    existing_messages = Message.objects.filter(chat=chat).count()
    
    
    last_user_message = Message.objects.filter(chat=chat, sender=request.user).last()
    last_message = Message.objects.filter(chat=chat).last()
    sent_message = Message.objects.create(chat=chat, sender=user, content=message)
    

    print("Sending notification")
    
    try:
            
        send_email = False        
                
        #Check it has been 10 minutes since the last message was sent or if another message has been sent in the chat by another user
        if last_message:
            if last_message.sender != request.user:
                send_email = True
        
        if last_user_message:
            time_difference = sent_message.timestamp - last_user_message.timestamp
            print (time_difference)
            if time_difference.seconds < 600:
                print("Less than 10 minutes since last message")
            else:
                print("More than 10 minutes since last message")
                send_email = True
        else:
            print ("No last message")
            send_email = True
                
        if send_email:
                
            superuser_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            organisation_admin_emails = OrganisationAdmin.objects.filter(organisation=chat.organisation).values_list('user__email', flat=True)
            emails = list(superuser_emails) + list(organisation_admin_emails)
            
            chat_user_emails = list(chat.participants.values_list('email', flat=True))
            
            #remove superusers and organisation admins
            chat_user_emails = [email for email in chat_user_emails if email not in emails]
            
            if len(chat_user_emails) > 2:
                request.method = "GET"
                return get_chat_content(request, chat_id, error=f"Something went wrong calculating the emails {len}")
            
            non_staff_emails = [email for email in chat_user_emails if email not in emails]
            
            for email in non_staff_emails:
                print ("Sending email to: " + email)
                if chat.chip_in_admins_chat:
                    SendChatEmailThread("Chip In", email, message).start()
                else:
                    SendChatEmailThread(chat.organisation.name, email, message).start()

        request.method = "GET"
        return get_chat_content(request, chat_id)
    except Exception as e:
        print('Error in communications (Admin Side)', e)
        request.method = "GET"
        return get_chat_content(request, chat_id)


def send_chat_email(organisation, recipient, message):
    subject = "Chip In: New Message from " + organisation
    message = f"""
Hello,

You have a new message from {organisation}.
Please login to the Chip In system to view and respond to the message.

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