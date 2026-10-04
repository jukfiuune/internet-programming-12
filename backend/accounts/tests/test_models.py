from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import Profile

User = get_user_model()


class UserModelTests(TestCase):
    def test_email_must_be_unique(self):
        User.objects.create_user(username="first", email="same@example.com", password="pw-12345678")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="second", email="same@example.com", password="pw-12345678")


class ProfileModelTests(TestCase):
    def test_profile_defaults_and_unique_nickname(self):
        user = User.objects.create_user(username="knight", email="knight@example.com", password="pw-12345678")
        profile = Profile.objects.create(user=user, nickname="Lancelot")

        self.assertEqual(user.profile, profile)
        self.assertEqual(profile.avatar_key, "knight-1")

        other = User.objects.create_user(username="other", email="other@example.com", password="pw-12345678")
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=other, nickname="Lancelot")
