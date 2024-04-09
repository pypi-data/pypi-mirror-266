"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from django.http import JsonResponse
from drf_spectacular.utils import inline_serializer, extend_schema
from health_check.backends import BaseHealthCheckBackend
from health_check.mixins import CheckMixin
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

__all__ = ['HealthChecks']


class HealthChecks(ViewSet, CheckMixin):
    """View for rendering system status messages"""

    permission_classes = []

    @staticmethod
    def render_to_response_json(plugins: dict[str, BaseHealthCheckBackend], status: int) -> JsonResponse:
        """Render a JSON response summarizing the status for a list of plugins

        Args:
            plugins: A list of plugins to render the status for
            status: The overall system status

        Returns:
            A JSON HTTP response
        """

        data = dict()
        for plugin_name, plugin in plugins.items():
            data[plugin_name] = {
                'status': 200 if plugin.status else 500,
                'message': plugin.pretty_status(),
                'time': plugin.time_taken,
                'critical_service': plugin.critical_service
            }

        return JsonResponse(data=data, status=status)

    @extend_schema(responses={'2XX': inline_serializer('success', dict())})
    def list(self, request: Request, *args, **kwargs) -> JsonResponse:
        """Return a JSON response detailing system status checks.

        The returned status code will be 200 if all checks pass. If any checks
        fail, the status code will be 500.
        """

        # This method functions similarly to the overloaded parent method,
        # except responses are forced to be JSON and never rendered HTML.

        status_code = 500 if self.errors else 200
        return self.render_to_response_json(self.plugins, status_code)
