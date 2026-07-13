from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="minseo",
            email="minseo@example.com",
            password="StrongPass123!",
            name="김민서",
            birth_date="2000-01-01",
        )

    def test_check_username(self):
        response = self.client.get(
            reverse("accounts:check-username"),
            {"username": "minseo"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["exists"])
        self.assertFalse(response.data["data"]["available"])

    def test_check_email(self):
        response = self.client.get(
            reverse("accounts:check-email"),
            {"email": "new@example.com"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(response.data["data"]["exists"])
        self.assertTrue(response.data["data"]["available"])

    def test_signup(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "name": "새유저",
                "birth_date": "2001-02-03",
                "password": "NewStrongPass123!",
                "password_confirm": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertNotIn("password", response.data["data"])

    def test_signup_rejects_duplicate_username(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "minseo",
                "email": "duplicate@example.com",
                "name": "중복",
                "birth_date": "2001-02-03",
                "password": "NewStrongPass123!",
                "password_confirm": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("username", response.data["data"])

    def test_login_and_logout(self):
        login_response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "minseo",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue(login_response.data["success"])

        logout_response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertTrue(logout_response.data["success"])

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "minseo",
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_me_requires_login(self):
        response = self.client.get(reverse("users:me"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        self.assertIn("message", response.data)

    def test_get_me(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("users:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "minseo")
        self.assertNotIn("password", response.data["data"])

    def test_me_does_not_allow_patch(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            reverse("users:me"),
            {"name": "수정된이름"},
            format="json",
        )
        self.user.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertFalse(response.data["success"])
        self.assertEqual(self.user.username, "minseo")
        self.assertEqual(self.user.name, "김민서")

    def test_update_ui_mode(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            reverse("users:ui-mode"),
            {"ui_mode": User.UIMode.EASY},
            format="json",
        )
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(self.user.ui_mode, User.UIMode.EASY)

    def test_update_ui_mode_rejects_invalid_value(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            reverse("users:ui-mode"),
            {"ui_mode": "INVALID"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("ui_mode", response.data["data"])

# Create your tests here.
