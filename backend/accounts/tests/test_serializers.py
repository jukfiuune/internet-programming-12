from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile
from accounts.serializers import ProfileSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


def registration_data(**overrides):
    data = {
        "username": "player_one",
        "email": "player@example.com",
        "nickname": "MountainKnight",
        "password": "example-password",
        "password_confirm": "example-password",
    }
    data.update(overrides)
    return data


class RegisterSerializerTests(TestCase):
    def test_uniqueness_checks_ignore_case(self):
        user = User.objects.create_user(username="Player_One", email="Player@Example.com", password="pw-12345678")
        Profile.objects.create(user=user, nickname="MOUNTAINKNIGHT")

        serializer = RegisterSerializer(data=registration_data())

        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), {"username", "email", "nickname"})

    def test_weak_password_is_rejected(self):
        serializer = RegisterSerializer(data=registration_data(password="12345", password_confirm="12345"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_passwords_are_write_only(self):
        serializer = RegisterSerializer(data=registration_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertNotIn("password", serializer.data)
        self.assertNotIn("password_confirm", serializer.data)
        self.assertTrue(user.check_password("example-password"))
        self.assertEqual(serializer.data["profile"]["nickname"], "MountainKnight")


class ProfileSerializerTests(TestCase):
    def test_rejects_unknown_avatar_and_taken_nickname(self):
        a = User.objects.create_user(username="a", email="a@example.com", password="pw-12345678")
        b = User.objects.create_user(username="b", email="b@example.com", password="pw-12345678")
        Profile.objects.create(user=a, nickname="Taken")
        profile_b = Profile.objects.create(user=b, nickname="Free")

        serializer = ProfileSerializer(profile_b, data={"nickname": "taken", "avatar_key": "dragon"}, partial=True)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), {"nickname", "avatar_key"})

    def test_keeping_own_nickname_is_valid(self):
        user = User.objects.create_user(username="a", email="a@example.com", password="pw-12345678")
        profile = Profile.objects.create(user=user, nickname="Mine")

        serializer = ProfileSerializer(profile, data={"nickname": "Mine"}, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)


class UserSerializerTests(TestCase):
    def test_output_contains_no_password_data(self):
        user = User.objects.create_user(username="a", email="a@example.com", password="pw-12345678")
        Profile.objects.create(user=user, nickname="Mine")

        data = UserSerializer(user).data

        self.assertEqual(set(data), {"id", "username", "email", "profile"})
