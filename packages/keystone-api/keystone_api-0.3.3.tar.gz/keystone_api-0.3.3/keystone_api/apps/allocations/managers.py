"""Custom database managers for encapsulating repeatable table queries.

Manager classes encapsulate common database operations at the table level (as
opposed to the level of individual records). At least one Manager exists for
every database model. Managers are commonly exposed as an attribute of the
associated model class called `objects`.
"""

from django.contrib.auth.models import User
from django.db import models

from apps.users.models import ResearchGroup

__all__ = ['AllocationManager', 'AllocationRequestManager', 'AllocationRequestReviewManager']


class AllocationManager(models.Manager):
    """Object manager for the `Allocation` database model"""

    def affiliated_with_user(self, user: User) -> models.QuerySet:
        """Get all allocations affiliated with the given user

        Args:
            user: The user to return affiliated records for

        Return:
            A filtered queryset
        """

        research_groups = ResearchGroup.objects.groups_for_user(user)
        return self.get_queryset().filter(request__group__in=research_groups)


class AllocationRequestManager(models.Manager):
    """Object manager for the `AllocationRequest` database model"""

    def affiliated_with_user(self, user: User) -> models.QuerySet:
        """Get all allocation requests affiliated with the given user

        Args:
            user: The user to return affiliated records for

        Return:
            A filtered queryset
        """

        research_groups = ResearchGroup.objects.groups_for_user(user)
        return self.get_queryset().filter(group__in=research_groups)


class AllocationRequestReviewManager(models.Manager):
    """Object manager for the `AllocationRequestReview` database model"""

    def affiliated_with_user(self, user: User) -> models.QuerySet:
        """Get all allocation request reviews affiliated with the given user

        Args:
            user: The user to return affiliated records for

        Return:
            A filtered queryset
        """

        research_groups = ResearchGroup.objects.groups_for_user(user)
        return self.get_queryset().filter(request__group__in=research_groups)
