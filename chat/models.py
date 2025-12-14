from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    """
    Conversation entre 2 utilisateurs ou un groupe.
    """
    participants = models.ManyToManyField(User, related_name="conversations")
    est_groupe = models.BooleanField(default=False)
    nom_groupe = models.CharField(max_length=255, blank=True, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.est_groupe:
            return f"Groupe : {self.nom_groupe}"
        return f"Conversation {self.id}"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Texte'),
        ('image', 'Image'),
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
        ('file', 'Fichier'),
    ]

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    expediteur = models.ForeignKey(User, related_name="messages_emis", on_delete=models.CASCADE ,null=True, blank=True  )

    type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')

    # Contenu principal
    texte = models.TextField(null=True, blank=True)

    # Fichiers
    fichier = models.FileField(upload_to="chat/", null=True, blank=True)

    # Meta
    lu = models.BooleanField(default=False)
    envoye_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.type} de {self.expediteur}"
