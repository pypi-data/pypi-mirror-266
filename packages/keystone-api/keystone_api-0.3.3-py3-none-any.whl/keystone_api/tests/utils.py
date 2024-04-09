"""Custom testing utilities used to streamline common tests."""

from django.test import Client


class CustomAsserts:
    """Custom assert methods for testing responses from REST endpoints"""

    client: Client
    assertEqual: callable

    @staticmethod
    def _build_request_args(method: str, kwargs: dict) -> dict:
        """Isolate head and body arguments for a given HTTP method from a dict of arguments

        Args:
            method: The HTTP method to identify arguments for
            kwargs: A dictionary of arguments

        Return:
            A dictionary with formatted arguments
        """

        arg_names = ('data', 'headers')
        arg_values = (kwargs.get(f'{method}_body', None), kwargs.get(f'{method}_headers', None))
        return {name: value for name, value in zip(arg_names, arg_values) if arg_values is not None}

    def assert_http_responses(self, endpoint: str, **kwargs) -> None:
        """Execute a series of API calls and assert the returned status matches the given values

        Args:
            endpoint: The URL to perform requests against
            **<request>: The integer status code expected by the given request type (get, post, etc.)
            **<request>_body: The data to include in the request (get_body, post_body, etc.)
            **<request>_headers: Header values to include in the request (get_headers, post_headers, etc.)
        """

        http_methods = ['get', 'head', 'options', 'post', 'put', 'patch', 'delete', 'trace']
        for method in http_methods:
            expected_status = kwargs.get(method, None)
            http_method = getattr(self.client, method)
            http_args = self._build_request_args(method, kwargs)

            if expected_status is not None:
                request = http_method(endpoint, **http_args)
                self.assertEqual(
                    expected_status, request.status_code,
                    f'{method} request received {request.status_code} instead of {expected_status}')
