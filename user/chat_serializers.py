# user/serializers.py (ajoute au fichier existant)
from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "phone_number")

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("id", "conversation", "sender", "content", "message_type", "file", "image", "sent_at", "is_read")
        read_only_fields = ("sent_at", "sender", "is_read")

class ConversationSerializer(serializers.ModelSerializer):
    user1 = UserBriefSerializer(read_only=True)
    user2 = UserBriefSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "user1", "user2", "created_at", "last_activity", "last_message")

    def get_last_message(self, obj):
        last = obj.messages.order_by("-sent_at").first()
        if not last:
            return None
        return MessageSerializer(last).data
