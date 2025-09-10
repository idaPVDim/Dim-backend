from rest_framework import serializers
from .models import Incident, Maintenance, QuestionMaintenance, ReponseMaintenance
from user.serializers import ProfilClientSerializer, ProfilTechnicienSerializer
# Serializers pour la maintenance

class IncidentSerializer(serializers.ModelSerializer):
    client = ProfilClientSerializer(read_only=True)

    class Meta:
        model = Incident
        fields = ['id', 'installation', 'client', 'description', 'date_signalisation', 'status']


class MaintenanceSerializer(serializers.ModelSerializer):
    technicien = ProfilTechnicienSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Maintenance
        fields = [
            'id', 'incident', 'technicien', 'solution_proposee',
            'cout_estime', 'temps_estime_heure', 'date_intervention_prevue',
            'date_intervention_reelle', 'rapport_intervention_pdf'
        ]


class QuestionMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionMaintenance
        fields = ['id', 'texte_question', 'type_question']


class ReponseMaintenanceSerializer(serializers.ModelSerializer):
    question = QuestionMaintenanceSerializer(read_only=True)

    class Meta:
        model = ReponseMaintenance
        fields = [
            'id', 'incident', 'question', 'reponse', 'date_reponse',
            'repondu_par_client', 'repondu_par_technicien'
        ]
