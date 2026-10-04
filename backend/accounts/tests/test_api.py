from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Profile

User = get_user_model()

PASSWORD = "example-password"


def create_player(username="player_one", email="player@example.com", nickname="MountainKnight"):
    user = User.objects.create_user(username=username, email=email, password=PASSWORD)
    Profile.objects.create(user=user, nickname=nickname)
    return user


def registration_data(**overrides):
    data = {
        "username": "player_one",
        "email": "player@example.com",
        "nickname": "MountainKnight",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }
    data.update(overrides)
    return data


class RegistrationTests(APITestCase):
    url = reverse("auth-register")

    def test_successful_registration(self):
        response = self.client.post(self.url, registration_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="player_one")
        self.assertEqual(user.profile.nickname, "MountainKnight")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(
            response.json(),
            {
                "id": user.id,
                "username": "player_one",
                "email": "player@example.com",
                "profile": {"nickname": "MountainKnight", "avatar_key": "knight-1"},
            },
        )
        self.assertNotIn(PASSWORD, response.content.decode())

    def test_invalid_registration(self):
        create_player(username="taken", email="taken@example.com", nickname="TakenKnight")
        cases = [
            ("username", registration_data(username="taken")),
            ("email", registration_data(email="taken@example.com")),
            ("nickname", registration_data(nickname="TakenKnight")),
            ("password_confirm", registration_data(password_confirm="different-password")),
        ]
        for field, data in cases:
            with self.subTest(field=field):
                response = self.client.post(self.url, data, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.json()["errors"])
                self.assertEqual(User.objects.count(), 1)


class LoginTests(APITestCase):
    url = reverse("auth-login")
    me_url = reverse("auth-me")

    def setUp(self):
        self.user = create_player()

    def test_successful_login(self):
        response = self.client.post(self.url, {"username": "player_one", "password": PASSWORD}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sessionid", response.cookies)

        me = self.client.get(self.me_url)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.json()["id"], self.user.id)
        self.assertEqual(me.json()["username"], "player_one")

    def test_failed_login(self):
        response = self.client.post(self.url, {"username": "player_one", "password": "wrong"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.json())
        self.assertNotIn("sessionid", response.cookies)
        self.assertEqual(self.client.get(self.me_url).status_code, status.HTTP_403_FORBIDDEN)


class MePermissionTests(APITestCase):
    url = reverse("auth-me")

    def test_anonymous_access_is_denied(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("errors", response.json())

    def test_authenticated_user_sees_only_own_data(self):
        create_player(username="someone_else", email="else@example.com", nickname="OtherKnight")
        me = create_player()
        self.client.force_authenticate(me)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], me.id)
        self.assertEqual(response.json()["profile"]["nickname"], "MountainKnight")


class ProfileUpdateTests(APITestCase):
    url = reverse("auth-me")

    def test_update_profile_ignores_protected_fields(self):
        user = create_player()
        self.client.force_authenticate(user)

        response = self.client.patch(
            self.url,
            {
                "nickname": "NewKnight",
                "avatar_key": "knight-3",
                "is_staff": True,
                "is_superuser": True,
                "username": "hacker",
                "email": "hacker@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["profile"], {"nickname": "NewKnight", "avatar_key": "knight-3"})
        user.refresh_from_db()
        self.assertEqual(user.profile.nickname, "NewKnight")
        self.assertEqual(user.profile.avatar_key, "knight-3")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.username, "player_one")
        self.assertEqual(user.email, "player@example.com")


class LogoutTests(APITestCase):
    def test_logout_ends_session(self):
        create_player()
        self.client.login(username="player_one", password=PASSWORD)

        response = self.client.post(reverse("auth-logout"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(reverse("auth-me")).status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_logout_is_denied(self):
        response = self.client.post(reverse("auth-logout"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CsrfTests(APITestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_unsafe_request_requires_csrf_token(self):
        create_player()
        self.client.login(username="player_one", password=PASSWORD)
        url = reverse("auth-me")
        payload = {"nickname": "NewKnight"}

        without_token = self.client.patch(url, payload, format="json")
        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("errors", without_token.json())

        csrf = self.client.get(reverse("auth-csrf"))
        self.assertEqual(csrf.status_code, status.HTTP_204_NO_CONTENT)
        token = csrf.cookies["csrftoken"].value

        with_token = self.client.patch(url, payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)
        self.assertEqual(with_token.json()["profile"]["nickname"], "NewKnight")

    def test_public_login_requires_csrf_token(self):
        create_player()
        url = reverse("auth-login")
        credentials = {"username": "player_one", "password": PASSWORD}

        self.assertEqual(self.client.post(url, credentials, format="json").status_code, status.HTTP_403_FORBIDDEN)

        token = self.client.get(reverse("auth-csrf")).cookies["csrftoken"].value
        response = self.client.post(url, credentials, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
