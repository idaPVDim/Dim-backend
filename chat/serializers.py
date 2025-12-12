from rest_framework import serializers
from .models import Message, Conversation

class MessageSerializer(serializers.ModelSerializer):
    expediteur_detail = serializers.StringRelatedField(source='expediteur', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'expediteur',
            'expediteur_detail',
            'type',
            'texte',
            'fichier',
            'lu',
            'envoye_le'
        ]
        read_only_fields = ['expediteur']


class ConversationSerializer(serializers.ModelSerializer):
    participants_detail = serializers.StringRelatedField(source='participants', many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'participants',
            'participants_detail',
            'est_groupe',
            'nom_groupe',
            'cree_le'
        ]
