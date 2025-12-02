# user/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for one-to-one conversation.
    Authentication via token querystring ?token=...
    URL: ws://.../ws/chat/conversation/<conversation_id>/?token=ABC
    """

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"conversation_{self.conversation_id}"

        # authenticate user via token (from query string)
        token = self.scope['query_string'].decode().split("token=")[-1] if b"token=" in self.scope['query_string'] else None
        self.user = None
        if token:
            self.user = await database_sync_to_async(self.get_user_for_token)(token)

        if not self.user:
            await self.close(code=4001)
            return

        # check participation
        allowed = await database_sync_to_async(self.is_user_participant)(self.user, int(self.conversation_id))
        if not allowed:
            await self.close(code=4003)
            return

        # join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        data = json.loads(text_data)
        action = data.get("action", "send")
        if action == "send":
            content = data.get("content", "")
            msg_type = data.get("message_type", "text")
            # create message in DB
            msg = await database_sync_to_async(self.create_message)(int(self.conversation_id), self.user, content, msg_type)
            # broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": {
                        "id": msg.id,
                        "conversation": msg.conversation.id,
                        "sender": {
                            "id": self.user.id,
                            "email": self.user.email,
                            "first_name": getattr(self.user,'first_name',''),
                            "last_name": getattr(self.user,'last_name',''),
                        },
                        "content": msg.content,
                        "message_type": msg.message_type,
                        "sent_at": msg.sent_at.isoformat(),
                        "is_read": msg.is_read,
                    }
                }
            )
        elif action == "typing":
            # broadcast typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.typing", "user_id": self.user.id}
            )
        elif action == "read":
            message_id = data.get("message_id")
            await database_sync_to_async(self.mark_as_read)(message_id, self.user)
            # optionally notify others
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.read", "message_id": message_id, "user_id": self.user.id}
            )

    # handlers for group_send
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"type":"message", "data": event["message"]}))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({"type":"typing", "user_id": event.get("user_id")}))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({"type":"read", "message_id": event.get("message_id"), "user_id": event.get("user_id")}))

    # ----- sync helper methods -----
    def get_user_for_token(self, token_key):
        try:
            token = Token.objects.select_related("user").get(key=token_key)
            return token.user
        except Exception:
            return None

    def is_user_participant(self, user, conversation_id):
        try:
            conv = Conversation.objects.get(pk=conversation_id)
            return user.id in {conv.user1_id, conv.user2_id}
        except Conversation.DoesNotExist:
            return False

    def create_message(self, conversation_id, user, content, message_type="text"):
        conv = Conversation.objects.get(pk=conversation_id)
        msg = Message.objects.create(conversation=conv, sender=user, content=content, message_type=message_type)
        conv.last_activity = msg.sent_at
        conv.save(update_fields=["last_activity"])
        return msg

    def mark_as_read(self, message_id, user):
        try:
            msg = Message.objects.get(pk=message_id)
            msg.is_read = True
            msg.save(update_fields=["is_read"])
            return True
        except Message.DoesNotExist:
            return False
