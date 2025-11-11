import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_username = self.scope['url_route']['kwargs']['username']
        self.other_user = await self.get_user(self.other_username)
        
        if not self.other_user:
            await self.close()
            return

        # Create unique room name (sorted user IDs)
        user_ids = sorted([self.user.id, self.other_user.id])
        self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark user as online
        await self.set_user_online(self.user, True)
        
        # Notify other user that this user is online
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'is_online': True
            }
        )

    async def disconnect(self, close_code):
        # Mark user as offline
        await self.set_user_online(self.user, False)
        
        # Notify other user that this user is offline
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'is_online': False
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            message_content = data['message']
            
            # Save message to database
            message = await self.save_message(message_content)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': self.user.username,
                    'timestamp': message['timestamp'],
                    'message_id': message['id']
                }
            )
        
        elif message_type == 'typing':
            # Broadcast typing indicator
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'typing_indicator',
                    'username': self.user.username,
                    'is_typing': data.get('is_typing', False)
                }
            )
        
        elif message_type == 'read':
            # Mark messages as read
            message_id = data.get('message_id')
            if message_id:
                await self.mark_message_read(message_id)
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type': 'message_read',
                        'message_id': message_id,
                        'reader': self.user.username
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    async def typing_indicator(self, event):
        # Don't send typing indicator to the person who is typing
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    async def user_status(self, event):
        # Don't send status update to the user themselves
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'status',
                'username': event['username'],
                'is_online': event['is_online']
            }))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'message_id': event['message_id'],
            'reader': event['reader']
        }))

    @database_sync_to_async
    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.get_or_create_conversation(self.user, self.other_user)
        conversation.updated_at = timezone.now()
        conversation.save()
        
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        
        return {
            'id': message.id,
            'timestamp': message.timestamp.isoformat()
        }

    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if message.sender != self.user:
                message.mark_as_read()
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def set_user_online(self, user, is_online):
        profile = user.profile
        profile.is_online = is_online
        profile.last_seen = timezone.now()
        profile.save()