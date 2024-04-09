"""Tests for the `ResearchGroup` model"""

from django.test import TestCase

from apps.users.models import ResearchGroup
from apps.users.tests.utils import create_test_user


class GetAllMembers(TestCase):
    """Test fetching all group members via the `get_all_members` member"""

    def setUp(self):
        """Create temporary user accounts for use in tests"""

        self.pi = create_test_user(username='pi')
        self.admin1 = create_test_user(username='admin1')
        self.admin2 = create_test_user(username='admin2')
        self.member1 = create_test_user(username='unprivileged1')
        self.member2 = create_test_user(username='unprivileged2')

    def test_all_accounts_returned(self) -> None:
        """Test all group members are included in the returned list"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.admins.add(self.admin1)
        group.admins.add(self.admin2)
        group.members.add(self.member1)
        group.members.add(self.member2)

        expected_members = (self.pi, self.admin1, self.admin2, self.member1, self.member2)
        self.assertEqual(expected_members, group.get_all_members())


class GetPrivilegedMembers(TestCase):
    """Test fetching group members via the `get_privileged_members` member"""

    def setUp(self):
        """Create temporary user accounts for use in tests"""

        self.pi = create_test_user(username='pi')
        self.admin1 = create_test_user(username='admin1')
        self.admin2 = create_test_user(username='admin2')
        self.member1 = create_test_user(username='member1')
        self.member2 = create_test_user(username='member2')

    def test_pi_only(self) -> None:
        """Test returned group members for a group with a PI only"""

        group = ResearchGroup.objects.create(pi=self.pi)
        expected_members = (self.pi,)
        self.assertEqual(expected_members, group.get_privileged_members())

    def test_pi_with_admins(self) -> None:
        """Test returned group members for a group with a PI and admins"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.admins.add(self.admin1)
        group.admins.add(self.admin2)

        expected_members = (self.pi, self.admin1, self.admin2)
        self.assertEqual(expected_members, group.get_privileged_members())

    def test_pi_with_members(self) -> None:
        """Test returned group members for a group with a PI and unprivileged members"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.members.add(self.member1)
        group.members.add(self.member2)

        expected_members = (self.pi,)
        self.assertEqual(expected_members, group.get_privileged_members())

    def test_pi_with_admin_and_members(self) -> None:
        """Test returned group members for a group with a PI, admins, and unprivileged members"""

        group = ResearchGroup.objects.create(pi=self.pi)
        group.admins.add(self.admin1)
        group.admins.add(self.admin2)
        group.members.add(self.member1)
        group.members.add(self.member2)

        expected_members = (self.pi, self.admin1, self.admin2)
        self.assertEqual(expected_members, group.get_privileged_members())
