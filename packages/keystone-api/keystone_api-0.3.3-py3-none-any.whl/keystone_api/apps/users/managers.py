"""Custom database managers for encapsulating repeatable table queries.

Manager classes encapsulate common database operations at the table level (as
opposed to the level of individual records). At least one Manager exists for
every database model. Managers are commonly exposed as an attribute of the
associated model class called `objects`.
"""

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import BaseUserManager
from django.db import models

if TYPE_CHECKING:
    from apps.users.models import User

__all__ = ['ResearchGroupManager', 'UserManager']


class UserManager(BaseUserManager):
    """Object manager for the `User` database model"""

    def create_user(
        self, username: str, first_name: str, last_name: str, email: str, password: str, **extra_fields
    ) -> 'User':
        """Create and a new user account

        Args:
            username: The account username
            first_name: The user's first name
            last_name: The user's last name
            email: A valid email address
            password: The account password
            **extra_fields: See fields of the `models.User` class for other accepted arguments

        Return:
            The saved user account
        """

        email = self.normalize_email(email)
        user = self.model(username=username, first_name=first_name, last_name=last_name, email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(
        self, username: str, first_name: str, last_name: str, email: str, password: str, **extra_fields
    ) -> 'User':
        """Create and a new user account with superuser privileges

        Args:
            username: The account username
            first_name: The user's first name
            last_name: The user's last name
            email: A valid email address
            password: The account password
            **extra_fields: See fields of the `models.User` class for other accepted arguments

        Return:
            The saved user account
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('When creating a superuser you must set `is_staff=True`.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('When creating a superuser you must set  `is_superuser=True`.')

        return self.create_user(username, first_name, last_name, email, password, **extra_fields)


class ResearchGroupManager(models.Manager):
    """Object manager for the `ResearchGroup` database model"""

    def groups_for_user(self, user: 'User') -> models.QuerySet:
        """Get all research groups the user is affiliated with.

        Args:
            user: The user to return affiliate groups for

        Return:
            A filtered queryset
        """

        return self.get_queryset().filter(models.Q(pi=user.id) | models.Q(admins=user.id) | models.Q(members=user.id))
