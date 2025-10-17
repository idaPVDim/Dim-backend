from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class DimensionnementPvAPIView(APIView):
    def post(self, request):
        serializer = DimensionnementPvSerializer(data=request.data)
        if serializer.is_valid():
            resultat = serializer.save()
            return Response(resultat, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
