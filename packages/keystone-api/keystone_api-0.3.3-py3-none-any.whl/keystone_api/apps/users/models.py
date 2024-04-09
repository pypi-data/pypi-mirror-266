"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.contrib.auth import models as auth_models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone

from .managers import *

__all__ = ['ResearchGroup', 'User']


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    """Proxy model for the built-in django `User` model"""

    username = models.CharField('username', max_length=150, unique=True, validators=[UnicodeUsernameValidator()])
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)
    email = models.EmailField('email address')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField('staff status', default=False)
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    is_ldap_user = models.BooleanField('LDAP User', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']


class ResearchGroup(models.Model):
    """A user research group tied to a slurm account"""

    name = models.CharField(max_length=255)
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_group_pi')
    admins = models.ManyToManyField(User, related_name='research_group_admins', blank=True)
    members = models.ManyToManyField(User, related_name='research_group_unprivileged', blank=True)

    objects = ResearchGroupManager()

    def get_all_members(self) -> tuple[User]:
        """Return all research group members"""

        return (self.pi,) + tuple(self.admins.all()) + tuple(self.members.all())

    def get_privileged_members(self) -> tuple[User]:
        """Return all research group members with admin privileges"""

        return (self.pi,) + tuple(self.admins.all())

    def __str__(self) -> str:
        """Return the research group's account name"""

        return str(self.name)
