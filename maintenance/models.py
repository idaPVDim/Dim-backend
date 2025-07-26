from django.db import models
from installation.models import Installation
from user.models import ProfilTechnicien, ProfilClient

class Incident(models.Model):
    STATUS_CHOICES = (
        ('reported', 'Signalé'),
        ('diagnosed', 'Diagnostiqué'),
        ('solution_proposed', 'Solution proposée'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    )
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE, related_name='incidents')
    client = models.ForeignKey(ProfilClient, on_delete=models.CASCADE, related_name='incidents_signales', null=True, blank=True)
    description = models.TextField()
    date_signalisation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')

    def __str__(self):
        return f"Incident #{self.id} - Installation {self.installation.id} ({self.get_status_display()})"

class Maintenance(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='maintenances')
    technicien = models.ForeignKey(ProfilTechnicien, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances')
    solution_proposee = models.TextField(blank=True, null=True)
    cout_estime = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    temps_estime_heure = models.PositiveIntegerField(blank=True, null=True)
    date_intervention_prevue = models.DateTimeField(blank=True, null=True)
    date_intervention_reelle = models.DateTimeField(blank=True, null=True)
    rapport_intervention_pdf = models.FileField(upload_to='maintenance_reports/', blank=True, null=True)

    def __str__(self):
        return f"Maintenance Incident {self.incident.id} - Technicien {self.technicien.user.username if self.technicien else 'N/A'}"

class QuestionMaintenance(models.Model):
    TYPE_CHOICES = (
        ('diagnostic', 'Diagnostic initial'),
        ('follow_up', 'Suivi'),
    )
    texte_question = models.TextField()
    type_question = models.CharField(max_length=20, choices=TYPE_CHOICES, default='diagnostic')

    def __str__(self):
        return self.texte_question

class ReponseMaintenance(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='reponses_diagnostic')
    question = models.ForeignKey(QuestionMaintenance, on_delete=models.CASCADE)
    reponse = models.TextField()
    date_reponse = models.DateTimeField(auto_now_add=True)
    repondu_par_client = models.BooleanField(default=False)
    repondu_par_technicien = models.BooleanField(default=False)

    def __str__(self):
        return f"Réponse Incident {self.incident.id} - Question {self.question.id}"
