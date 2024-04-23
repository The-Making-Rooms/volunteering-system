from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Chat, Message
# Register your models here.

@admin.register(Chat)
class ChatAdmin(ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(ModelAdmin):
    pass