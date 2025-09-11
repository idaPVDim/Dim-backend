from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User

class LoginAPITest(APITestCase):
    def setUp(self):
        # Création d’un utilisateur test
        self.user_email = "testuser@example.com"
        self.user_password = "strongpassword123"
        self.user_role = "technicien"
        self.user = User.objects.create_user(
            email=self.user_email,
            password=self.user_password,
            role=self.user_role
        )
        self.login_url = reverse("login")  # Nommez correctement selon votre router/api

    def test_login_success(self):
        data = {
            "email": self.user_email,
            "password": self.user_password,
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], self.user_email)
        self.assertEqual(response.data["role"], self.user_role)

    def test_login_fail_wrong_password(self):
        data = {
            "email": self.user_email,
            "password": "wrongpassword",
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)  # Ou clé d’erreur appropriée
