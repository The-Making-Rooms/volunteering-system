"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.contrib import admin

from .models import Chat, Message
# Register your models here.

#Show the chat model in the admin panel with message inline
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    
class ChatAdmin(admin.ModelAdmin):
    inlines = [MessageInline]


admin.site.register(Chat, ChatAdmin)