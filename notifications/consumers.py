import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'conversation_{self.conversation_id}'

        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        is_participant = await self.is_user_participant(self.scope['user'], self.conversation_id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.conversation_group_name, self.channel_name)
        await self.accept()

        # Mark incoming messages as read and notify the sender
        marked = await self.mark_messages_read(self.scope['user'], self.conversation_id)
        if marked:
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'read_receipt',
                    'reader': self.scope['user'].username,
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.conversation_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message', '').strip()

        if not message_content:
            return

        message = await self.save_message(
            conversation_id=self.conversation_id,
            sender=self.scope['user'],
            content=message_content
        )

        message_data = await self.get_message_data(message.id)

        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def chat_message(self, event):
        message = dict(event['message'])
        # If this consumer's user is the recipient (not the sender) and is currently
        # connected to the chat, mark the message as read immediately so the unread
        # count doesn't grow while the user is viewing the conversation.
        if message.get('sender') != self.scope['user'].username:
            await self.mark_single_message_read(message['id'])
            message['is_read'] = True
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'read_receipt',
                    'reader': self.scope['user'].username,
                }
            )
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'reader': event['reader'],
        }))

    @database_sync_to_async
    def is_user_participant(self, user, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation.participant1 == user or conversation.participant2 == user
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_messages_read(self, user, conversation_id):
        """Mark all unread messages NOT sent by this user as read. Returns True if any were marked."""
        updated = Message.objects.filter(
            conversation_id=conversation_id,
            is_read=False
        ).exclude(sender=user).update(is_read=True)
        return updated > 0

    @database_sync_to_async
    def mark_single_message_read(self, message_id):
        Message.objects.filter(id=message_id, is_read=False).update(is_read=True)

    @database_sync_to_async
    def save_message(self, conversation_id, sender, content):
        return Message.objects.create(
            conversation_id=conversation_id,
            sender=sender,
            content=content
        )

    @database_sync_to_async
    def get_message_data(self, message_id):
        message = Message.objects.select_related('sender').get(id=message_id)
        return {
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'sender_first_name': message.sender.first_name,
            'timestamp': message.created_at.isoformat(),
            'is_read': message.is_read
        }
