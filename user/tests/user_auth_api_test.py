from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UserAuthAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        User.objects.create_user(email="tester1@example.com", nickname="김포카", password="111111")

    def test_register_user(self):
        param = {"email": "tester2@example.com", "nickname": "김포카2호", "password": "111111"}
        response = self.client.post("/api/users/auth/register/", param)
        print(f"response = {response.data}")

        self.assertEqual(response.data.get("user", {}).get("email"), param.get("email"))
        self.assertEqual(response.data.get("user", {}).get("nickname"), param.get("nickname"))

    def test_login_user(self):
        param = {"email": "tester1@example.com", "password": "111111"}
        response = self.client.post("/api/users/auth/login/", param)
        print(f"response = {response.data}")

        self.assertEqual(response.data.get("user", {}).get("email"), param.get("email"))
