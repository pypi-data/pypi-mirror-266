"""Tests for the `ResearchGroupManager` class"""

from django.test import TestCase

from apps.users.models import ResearchGroup
from apps.users.tests.utils import create_test_user


class GroupsForUser(TestCase):
    """Test fetching group affiliations via the `groups_for_user` method"""

    def setUp(self):
        """Create temporary users and groups"""

        self.test_user = create_test_user(username='test_user')
        other_user = create_test_user(username='other_user')

        # Group where the test user is PI
        self.group1 = ResearchGroup.objects.create(name='Group1', pi=self.test_user)

        # Group where the test user is an admin
        self.group2 = ResearchGroup.objects.create(name='Group2', pi=other_user)
        self.group2.members.add(self.test_user)

        # Group where the test user is an unprivileged member
        self.group3 = ResearchGroup.objects.create(name='Group3', pi=other_user)
        self.group3.members.add(self.test_user)

        # Group where the test user has no role
        self.group4 = ResearchGroup.objects.create(name='Group4', pi=other_user)

    def test_groups_for_user(self) -> None:
        """Test all groups are returned for a test user"""

        result = ResearchGroup.objects.groups_for_user(self.test_user).all()
        self.assertCountEqual(result, [self.group1, self.group2, self.group3])
