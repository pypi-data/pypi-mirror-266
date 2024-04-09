"""Tests for the `/health/` endpoint"""

import logging

from django.test import TransactionTestCase
from rest_framework import status

from apps.users.tests.utils import create_test_user


class EndpointPermissions(TransactionTestCase):
    """Test endpoint user permissions

    Endpoint permissions are tested against the following matrix of HTTP responses.

    | Authentication      | GET     | HEAD     | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |---------------------|---------|----------|---------|------|-----|-------|--------|-------|
    | Anonymous User      | 200/500 | 200/500  | 200/500 | 405  | 405 | 405   | 405    | 405   |
    | Authenticated User  | 200/500 | 200/500  | 200/500 | 405  | 405 | 405   | 405    | 405   |
    | Staff User          | 200/500 | 200/500  | 200/500 | 405  | 405 | 405   | 405    | 405   |
    """

    endpoint = '/health/'
    fixtures = ['multi_research_group.yaml']
    valid_responses = (status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def assert_read_only_responses(self) -> None:
        """Assert the currently authenticated user has read only permissions"""

        # Temporarily disable health check logging
        # Avoids spamming the console with health check messages
        health_check_log = logging.getLogger('health-check')
        log_level = health_check_log.level
        health_check_log.setLevel(1000)

        self.assertIn(self.client.get(self.endpoint).status_code, self.valid_responses)
        self.assertIn(self.client.head(self.endpoint).status_code, self.valid_responses)
        self.assertIn(self.client.options(self.endpoint).status_code, self.valid_responses)

        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Restore the health chck logger
        health_check_log.setLevel(log_level)

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users have read-only access"""

        self.assert_read_only_responses()

    def test_authenticated_user_permissions(self) -> None:
        """Test general authenticated users are returned a 403 status code for all request types"""

        create_test_user(username='foo', password='foobar123!')
        self.assertTrue(self.client.login(username='foo', password='foobar123!'))
        self.assert_read_only_responses()

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read-only permissions"""

        create_test_user(username='foo', password='foobar123!')
        self.assertTrue(self.client.login(username='foo', password='foobar123!'))
        self.assert_read_only_responses()
