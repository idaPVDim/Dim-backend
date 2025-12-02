# user/views_chat.py
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserBriefSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by("-last_activity")
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(models.Q(user1=user) | models.Q(user2=user)).order_by("-last_activity")

    def create(self, request, *args, **kwargs):
        # create or get conversation between current user and target user_id
        target_id = request.data.get("user_id")
        if not target_id:
            return Response({"detail": "user_id required"}, status=status.HTTP_400_BAD_REQUEST)
        target = get_object_or_404(User, pk=target_id)
        conv, created = Conversation.get_or_create_between(request.user, target)
        serializer = self.get_serializer(conv)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def messages(self, request, pk=None):
        conv = self.get_object()
        # permission: only participants can view
        if request.user not in [conv.user1, conv.user2]:
            return Response({"detail":"Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        qs = conv.messages.order_by("sent_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageSerializer(qs, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("-sent_at")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # send message via REST (also channels consumer should broadcast when websocket used)
        serializer.save(sender=self.request.user)
        # update conversation last_activity
        conv = serializer.instance.conversation
        conv.last_activity = serializer.instance.sent_at
        conv.save()
