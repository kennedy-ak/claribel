from django.contrib import admin
from .models import Notification, Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ['sender', 'content', 'is_read', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'trigger_event', 'notification_type', 'subject', 'sent_successfully', 'sent_at']
    list_filter = ['notification_type', 'trigger_event', 'sent_successfully']
    search_fields = ['recipient__username', 'subject', 'message']
    date_hierarchy = 'sent_at'
    readonly_fields = ['recipient', 'notification_type', 'trigger_event', 'subject', 'message', 'sent_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'created_at', 'updated_at', 'get_message_count']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participant1__username', 'participant2__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageInline]

    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'content']
    date_hierarchy = 'created_at'
    readonly_fields = ['conversation', 'sender', 'content', 'created_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
