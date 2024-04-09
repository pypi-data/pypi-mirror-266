"""Tests for application views"""

from unittest.mock import MagicMock

from django.http import JsonResponse
from django.test import TestCase

from apps.health.views import HealthChecks


class TestHealthChecks(TestCase):
    """Test the rendering of application health checks"""

    @staticmethod
    def create_mock_plugin(
        identifier: str, status: int, pretty_status: str, time_taken: float, critical_service: bool
    ) -> MagicMock:
        """Create a mock health check plugin

        Args:
            identifier: The health check identifier
            status: The health check status
            pretty_status: The health check status message
            time_taken: Time taken to perform the health check
            critical_service: Whether the health check represents a critical service

        Return:
            A MagicMock object
        """

        mock_plugin = MagicMock()
        mock_plugin.identifier.return_value = identifier
        mock_plugin.status = status
        mock_plugin.pretty_status.return_value = pretty_status
        mock_plugin.time_taken = time_taken
        mock_plugin.critical_service = critical_service
        return mock_plugin

    def test_render_response_to_json_500(self) -> None:
        """Test the rendered response has a 500 status when a health check fails"""

        expected_data = {
            'plugin1': {
                'identifier': 'plugin1',
                'status': 200,
                'pretty_status': 'OK',
                'time_taken': 1.0,
                'critical_service': True
            },
            'plugin2': {
                'identifier': 'plugin2',
                'status': 500,
                'pretty_status': 'Error',
                'time_taken': 2.0,
                'critical_service': False
            }
        }

        health_checks = {
            'plugin1': self.create_mock_plugin(**expected_data['plugin1']),
            'plugin2': self.create_mock_plugin(**expected_data['plugin2'])
        }

        response = HealthChecks.render_to_response_json(health_checks, 500)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)

    def test_render_response_to_json_200(self) -> None:
        """Test the rendered response has a 200 status when all health checks pass"""

        expected_data = {
            'plugin1': {
                'identifier': 'plugin1',
                'status': 200,
                'pretty_status': 'OK',
                'time_taken': 1.0,
                'critical_service': True
            },
            'plugin2': {
                'identifier': 'plugin2',
                'status': 200,
                'pretty_status': 'OK',
                'time_taken': 2.0,
                'critical_service': False
            }
        }

        health_checks = {
            'plugin1': self.create_mock_plugin(**expected_data['plugin1']),
            'plugin2': self.create_mock_plugin(**expected_data['plugin2'])
        }

        response = HealthChecks.render_to_response_json(health_checks, 500)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)
