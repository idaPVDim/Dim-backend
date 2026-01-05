import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Conversation, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Vérifier si l'utilisateur est connecté
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        # Vérifier s'il appartient à la conversation
        is_member = await self.check_membership()
        if not is_member:
            await self.close()
            return

        # Rejoindre la room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # ===============================================
    # Receive message from WebSocket
    # ===============================================
    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "message":
            await self.handle_message(data)

        elif event_type == "seen":
            await self.handle_seen(data)

    # =====================================================
    # HANDLE MESSAGE
    # =====================================================
    async def handle_message(self, data):
        text = data.get("text", "")
        message_type = data.get("message_type", "text")
        media_file = None

        # Enregistrer le message en DB
        msg = await self.create_message(text, message_type, media_file)

        # Diffuser à tous les utilisateurs de la conversation
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "id": msg["id"],
                    "sender": msg["sender"],
                    "text": msg["text"],
                    "message_type": msg["message_type"],
                    "created_at": msg["created_at"]
                }
            }
        )

    # Message reçu dans un autre client → renvoyé au frontend
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    # =====================================================
    # HANDLE "SEEN" (message lu)
    # =====================================================
    async def handle_seen(self, data):
        message_id = data.get("message_id")
        await self.mark_message_seen(message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_seen",
                "message_id": message_id,
                "seen_by": self.scope["user"].id
            }
        )

    async def chat_seen(self, event):
        await self.send(text_data=json.dumps({
            "type": "seen",
            "message_id": event["message_id"],
            "seen_by": event["seen_by"],
        }))

    # =====================================================
    # DATABASE OPERATIONS
    # =====================================================

    @database_sync_to_async
    def check_membership(self):
        try:
            convo = Conversation.objects.get(id=self.conversation_id)
            return self.scope["user"] in convo.participants.all()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, text, message_type, media_file):
        conversation = Conversation.objects.get(id=self.conversation_id)
        sender = self.scope["user"]

        msg = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text,
            message_type=message_type,
            media_file=media_file
        )

        # Créer des notifications
        for user in conversation.participants.exclude(id=sender.id):
            MessageNotification.objects.create(
                user=user,
                message=msg
            )

        return {
            "id": msg.id,
            "sender": sender.id,
            "text": msg.text,
            "message_type": msg.message_type,
            "created_at": str(msg.created_at)
        }

    @database_sync_to_async
    def mark_message_seen(self, message_id):
        Message.objects.filter(id=message_id).update(is_seen=True)
        MessageNotification.objects.filter(message_id=message_id).update(is_read=True)
