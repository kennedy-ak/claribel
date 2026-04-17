import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'conversation_{self.conversation_id}'

        # Check if user is authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        # Verify user is part of this conversation
        is_participant = await self.is_user_participant(self.scope['user'], self.conversation_id)
        if not is_participant:
            await self.close()
            return

        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave conversation group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message', '').strip()

        if not message_content:
            return

        # Save message to database
        message = await self.save_message(
            conversation_id=self.conversation_id,
            sender=self.scope['user'],
            content=message_content
        )

        # Get message data for WebSocket
        message_data = await self.get_message_data(message.id)

        # Send message to conversation group
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def is_user_participant(self, user, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation.participant1 == user or conversation.participant2 == user
        except Conversation.DoesNotExist:
            return False

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