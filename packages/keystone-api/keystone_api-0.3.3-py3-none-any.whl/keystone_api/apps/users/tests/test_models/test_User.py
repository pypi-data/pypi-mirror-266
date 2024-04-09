"""Tests for the `User` class"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.models import User


class UserModelRegistration(TestCase):
    """Test the registration of the model with the Django authentication system"""

    def test_registered_as_default_user_model(self) -> None:
        """Test the `User` class is returned by the built-in `get_user_model` method"""

        self.assertIs(User, get_user_model())
