from django.db import models
from django.conf import settings


# ==========================================================
# CONVERSATION (entre 2 utilisateurs)
# ==========================================================
class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        usernames = " - ".join([u.username for u in self.participants.all()])
        return f"Conversation ({usernames})"


# ==========================================================
# MESSAGE
# ==========================================================
class Message(models.Model):

    MESSAGE_TYPES = (
        ('text', 'Texte'),
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
        ('file', 'Fichier'),
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent"
    )

    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default='text'
    )

    text = models.TextField(null=True, blank=True)
    media_file = models.FileField(
        upload_to="chat/media/",
        null=True,
        blank=True
    )

    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} ({self.message_type})"


# ==========================================================
# NOTIFICATION MESSAGE (optionnel)
# ==========================================================
class MessageNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_notifications"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif -> {self.user.username}"
