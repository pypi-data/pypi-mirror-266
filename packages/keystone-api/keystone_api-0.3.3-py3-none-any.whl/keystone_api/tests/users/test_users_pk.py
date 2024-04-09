"""Tests for the `/users/users/<pk>/` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from tests.utils import CustomAsserts


class EndpointPermissions(APITestCase, CustomAsserts):
    """Test endpoint user permissions

    Permissions depend on whether the user is a member of the record's associated research group.

    Endpoint permissions are tested against the following matrix of HTTP responses.

    | Authentication              | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |-----------------------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous User             | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | User accessing own user    | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | User accessing other user  | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Staff User                 | 200 | 200  | 200     | 405  | 200 | 200   | 204    | 405   |
    """

    endpoint_pattern = '/users/users/{pk}/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users cannot access resources"""

        endpoint = self.endpoint_pattern.format(pk=1)
        self.assert_http_responses(
            endpoint,
            get=status.HTTP_401_UNAUTHORIZED,
            head=status.HTTP_401_UNAUTHORIZED,
            options=status.HTTP_401_UNAUTHORIZED,
            post=status.HTTP_401_UNAUTHORIZED,
            put=status.HTTP_401_UNAUTHORIZED,
            patch=status.HTTP_401_UNAUTHORIZED,
            delete=status.HTTP_401_UNAUTHORIZED,
            trace=status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_same_user(self) -> None:
        """Test permissions for authenticated users accessing their own user record"""

        # Define a user / record endpoint from the SAME user
        endpoint = self.endpoint_pattern.format(pk=3)
        user = User.objects.get(username='member_1')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_403_FORBIDDEN,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
            put_body={'username': 'member_3', 'first_name': 'foo', 'last_name': 'bar', 'email': 'member_3@domain.com',
                      'password': 'foobar123'},
            patch_body={'email': 'member_3@newdomain.com'},
        )

    def test_authenticated_user_different_user(self) -> None:
        """Test permissions for authenticated users accessing records of another user"""

        # Define a user / record endpoint from a DIFFERENT user
        endpoint = self.endpoint_pattern.format(pk=1)
        user = User.objects.get(username='member_2')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_403_FORBIDDEN,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
        )

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read and write permissions"""

        endpoint = self.endpoint_pattern.format(pk=1)
        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_405_METHOD_NOT_ALLOWED,
            put=status.HTTP_200_OK,
            patch=status.HTTP_200_OK,
            delete=status.HTTP_204_NO_CONTENT,
            trace=status.HTTP_405_METHOD_NOT_ALLOWED,
            put_body={'username': 'member_3', 'first_name': 'foo', 'last_name': 'bar', 'email': 'member_3@domain.com',
                      'password': 'foobar123'},
            patch_body={'email': 'member_3@newdomain.com'},
        )
