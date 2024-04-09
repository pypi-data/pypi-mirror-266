"""Tests for the `/allocations/requests/` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from tests.utils import CustomAsserts


class EndpointPermissions(APITestCase, CustomAsserts):
    """Test endpoint user permissions

    Endpoint permissions are tested against the following matrix of HTTP responses.

    | Authentication | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |----------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous User | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | Non-Member     | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Group Member   | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Group Admin    | 200 | 200  | 200     | 201  | 403 | 403   | 403    | 403   |
    | Group PI       | 200 | 200  | 200     | 201  | 403 | 403   | 403    | 403   |
    | Staff User     | 200 | 200  | 200     | 201  | 405 | 405   | 405    | 405   |
    """

    endpoint = '/allocations/requests/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users cannot access resources"""

        self.assert_http_responses(
            self.endpoint,
            get=status.HTTP_401_UNAUTHORIZED,
            head=status.HTTP_401_UNAUTHORIZED,
            options=status.HTTP_401_UNAUTHORIZED,
            post=status.HTTP_401_UNAUTHORIZED,
            put=status.HTTP_401_UNAUTHORIZED,
            patch=status.HTTP_401_UNAUTHORIZED,
            delete=status.HTTP_401_UNAUTHORIZED,
            trace=status.HTTP_401_UNAUTHORIZED
        )

    def test_non_group_member_permissions(self) -> None:
        """Test users have read access but cannot create records for research groups where they are not members"""

        user = User.objects.get(username='generic_user')
        self.client.force_authenticate(user=user)

        # Post data reflects a group ID for which the user is not a member
        self.assert_http_responses(
            self.endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_403_FORBIDDEN,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
            post_body={'title': 'foo', 'description': 'bar', 'group': 1}
        )

    def test_group_member_permissions(self) -> None:
        """Test regular research group members have read-only access"""

        user = User.objects.get(username='member_1')
        self.client.force_authenticate(user=user)

        # Post data reflects a group ID for which the user is a regular member
        self.assert_http_responses(
            self.endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_403_FORBIDDEN,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
            post_body={'title': 'foo', 'description': 'bar', 'group': 1}
        )

    def test_group_admin_permissions(self) -> None:
        """Test research group admins have read and write access"""

        user = User.objects.get(username='group_admin_1')
        self.client.force_authenticate(user=user)

        # Post data reflects a group ID for which the user is an admin
        self.assert_http_responses(
            self.endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_201_CREATED,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
            post_body={'title': 'foo', 'description': 'bar', 'group': 1}
        )

    def test_group_pi_permissions(self) -> None:
        """Test research group PIs have read and write access"""

        user = User.objects.get(username='pi_1')
        self.client.force_authenticate(user=user)

        # Post data reflects a group ID for which the user is a PI
        self.assert_http_responses(
            self.endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_201_CREATED,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
            post_body={'title': 'foo', 'description': 'bar', 'group': 1}
        )

    def test_staff_user(self) -> None:
        """Test staff users have read and write permissions"""

        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            self.endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_201_CREATED,
            put=status.HTTP_405_METHOD_NOT_ALLOWED,
            patch=status.HTTP_405_METHOD_NOT_ALLOWED,
            delete=status.HTTP_405_METHOD_NOT_ALLOWED,
            trace=status.HTTP_405_METHOD_NOT_ALLOWED,
            post_body={'title': 'foo', 'description': 'bar', 'group': 1}
        )
