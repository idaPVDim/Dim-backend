from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Autorise uniquement les admins."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsSelf(BasePermission):
    """Autorise l'utilisateur à modifier seulement son propre compte."""
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdminOrSelf(BasePermission):
    """Admin ou propriétaire du compte."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class IsTechnicien(BasePermission):
    """Autorise uniquement les techniciens."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "technicien"


class IsClient(BasePermission):
    """Autorise uniquement les clients."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"


class IsMarchand(BasePermission):
    """Autorise uniquement les marchands."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "marchand"


class ReadOnly(BasePermission):
    """Toujours autorisé en lecture seule (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
