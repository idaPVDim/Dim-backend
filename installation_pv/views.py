from rest_framework import generics, permissions
from .models import DimensionnementPV
from .serializers import DimensionnementPVSerializer

class DimensionnementPVListCreateView(generics.ListCreateAPIView):
    queryset = DimensionnementPV.objects.all()
    serializer_class = DimensionnementPVSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profilclient'):
            return self.queryset.filter(installation__client__user=user)
        elif hasattr(user, 'profiltechnicien'):
            return self.queryset.filter(installation__technicien__user=user)
        return self.queryset.none()


class DimensionnementPVDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DimensionnementPV.objects.all()
    serializer_class = DimensionnementPVSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profilclient'):
            return self.queryset.filter(installation__client__user=user)
        elif hasattr(user, 'profiltechnicien'):
            return self.queryset.filter(installation__technicien__user=user)
        return self.queryset.none()
