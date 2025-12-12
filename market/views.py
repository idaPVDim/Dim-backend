# market/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TechnicalRequest, TechnicalRequestItem, VendorQuote, VendorQuoteItem, SelectedVendorQuote
from .serializers import TechnicalRequestSerializer, VendorQuoteSerializer
from user.models import ProfilMarchand, ProfilTechnicien
from django.shortcuts import get_object_or_404
from django.db import transaction
from chat.models import Conversation  # ton app chat existante

class IsTechnicienOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or getattr(request.user, "profil_technicien", None) is not None

class TechnicalRequestViewSet(viewsets.ModelViewSet):
    queryset = TechnicalRequest.objects.all().order_by("-date_creation")
    serializer_class = TechnicalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # technicien voit ses requests; admin voit tout ; marchands voient celles qui les concernent; client voit celles de ses installations
        if user.is_staff:
            return self.queryset
        if getattr(user, "profil_technicien", None):
            return self.queryset.filter(technicien=user.profil_technicien)
        if getattr(user, "profil_marchand", None):
            return self.queryset.filter(destinataires=user.profil_marchand) | self.queryset.filter(vendor_quotes__marchant=user.profil_marchand)
        if getattr(user, "profil_client", None):
            return self.queryset.filter(installation__client=user.profil_client)
        return TechnicalRequest.objects.none()

    def perform_create(self, serializer):
        # createur is set in serializer.create
        return super().perform_create(serializer)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsTechnicienOrAdmin])
    def send_to_marchands(self, request, pk=None):
        """
        Endpoint to send/broadcast the technical request to:
         - either list of marchands provided in body: {"marchand_ids":[1,2]}
         - or broadcast (if no marchand_ids) to matched marchands (zone)
        It sets date_envoi and statut='sent'
        """
        tr = self.get_object()
        marchand_ids = request.data.get("marchand_ids", None)
        if marchand_ids:
            marchands = ProfilMarchand.objects.filter(id__in=marchand_ids)
            tr.destinataires.set(marchands)
        else:
            # simple default: all marchands (you can filter by zone later)
            marchands = ProfilMarchand.objects.all()
            tr.destinataires.set(marchands)

        tr.statut = "sent"
        tr.date_envoi = timezone.now()
        tr.save()

        # Optionally create conversation per marchant (tech <-> marchant)
        try:
            tech_user = tr.createur
            for pm in tr.destinataires.all():
                # create conversation if not exists between tech_user and marchant.user
                participants = [tech_user, pm.user]
                conv = Conversation.objects.filter(participants=tech_user).filter(participants=pm.user).first()
                if not conv:
                    conv = Conversation.objects.create()
                    conv.participants.set(participants)
        except Exception:
            pass

        return Response({"detail": "Request sent", "destinataires": [m.id for m in tr.destinataires.all()]}, status=200)

class VendorQuoteViewSet(viewsets.ModelViewSet):
    queryset = VendorQuote.objects.all().order_by("-date_reponse")
    serializer_class = VendorQuoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        if getattr(user, "profil_marchand", None):
            return self.queryset.filter(marchant=user.profil_marchand)
        if getattr(user, "profil_technicien", None):
            return self.queryset.filter(technical_request__technicien=user.profil_technicien)
        return VendorQuote.objects.none()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        vq = self.get_object()
        # Only technicien or admin can accept a vendor quote (to be selected for devis)
        if not (request.user.is_staff or getattr(request.user, "profil_technicien", None)):
            return Response({"detail":"Forbidden"}, status=403)
        with transaction.atomic():
            # mark accepted and create SelectedVendorQuote
            vq.statut = "accepted"
            vq.save()
            tr = vq.technical_request
            SelectedVendorQuote.objects.update_or_create(technical_request=tr, defaults={"vendor_quote": vq, "selected_by": request.user})
            # convert to Devis (client quote) - we will leave creation to a dedicated endpoint (see below)
        return Response({"detail":"VendorQuote accepted"}, status=200)
