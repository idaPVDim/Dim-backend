from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Conversation, Message, MessageNotification
from .serializers import (
    ConversationSerializer, MessageSerializer, MessageNotificationSerializer
)

User = get_user_model()


# ==========================================================
# CONVERSATION VIEWSET
# ==========================================================
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Créer une nouvelle conversation entre deux utilisateurs."""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)

        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Vérifier si une conversation existe déjà
        convo = Conversation.objects.filter(participants=request.user)\
                                    .filter(participants=other_user)\
                                    .first()

        if convo:
            return Response(ConversationSerializer(convo).data)

        # Créer une nouvelle conversation
        convo = Conversation.objects.create()
        convo.participants.add(request.user, other_user)

        return Response(ConversationSerializer(convo).data, status=201)


# ==========================================================
# MESSAGE VIEWSET
# ==========================================================
class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

        # Créer les notifications pour les destinataires
        message = serializer.instance
        for user in message.conversation.participants.exclude(id=message.sender.id):
            MessageNotification.objects.create(user=user, message=message)

    @action(detail=True, methods=['post'])
    def seen(self, request, pk=None):
        """Marquer un message comme vu."""
        message = self.get_object()

        if message.sender == request.user:
            return Response({"error": "Sender cannot mark message as seen"}, status=403)

        message.is_seen = True
        message.save()

        # Marquer la notification comme lue
        MessageNotification.objects.filter(user=request.user, message=message).update(is_read=True)

        return Response({"success": True})
    

# ==========================================================
# NOTIFICATION VIEWSET
# ==========================================================
class MessageNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = MessageNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageNotification.objects.filter(user=self.request.user)
