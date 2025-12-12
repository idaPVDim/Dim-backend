# installation/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Devis.emetteur ou destinataire peut accéder
        if request.user.is_staff:
            return True
        return getattr(obj, "emetteur", None) == request.user or getattr(obj, "destinataire", None) == request.user

class IsTechnicien(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "technicien"

class IsMarchand(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "marchant"

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"
