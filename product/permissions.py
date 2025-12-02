from rest_framework.permissions import BasePermission

class IsMarchandOwner(BasePermission):
    message = "Vous n'avez pas la permission de gérer cet équipement."

    def has_object_permission(self, request, view, obj):
        return obj.marchant == getattr(request.user, "profil_marchand", None)
