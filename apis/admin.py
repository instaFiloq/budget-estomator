from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'project_id', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('role', 'content_short', 'conversation', 'created_at')
    
    def content_short(self, obj):
        return obj.content[:50]
    content_short.short_description = 'Content'