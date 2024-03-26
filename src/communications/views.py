from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Chat, Message
from commonui.views import check_if_hx, HTTPResponseHXRedirect
from webpush import send_user_notification
from django.conf import settings
# Create your views here.


def index(request):
    user = request.user
    chats = Chat.objects.filter(participants=user)
    return render(request, 'communications/index.html', {
        'hx': check_if_hx(request),
        'chats': chats,
        'link_active': 'communications'
    })
 
def get_chat_content(request, chat_id):
    user = request.user
    chat = Chat.objects.get(id=chat_id)
    
    if user not in chat.participants.all():
        return HTTPResponseHXRedirect('/communications')

    messages = Message.objects.filter(chat=chat)
    return render(request, 'communications/chat.html', {
        'hx': check_if_hx(request),
        'chat': chat,
        'messages': messages,
        'user': user.id,
        'link_active': 'communications'
    })

def send_message(request, chat_id):
    if request.method != 'POST':
        return HTTPResponseHXRedirect('/communications')
    
    if request.POST['message'] == '':
        return get_chat_content(request, chat_id)

    
    user = request.user
    chat = Chat.objects.get(id=chat_id)

    if user not in chat.participants.all():
        return HTTPResponseHXRedirect('/communications')
    
    

    message = request.POST['message']
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