"""Custom permission objects used to manage access to HTTP endpoints.

Permission classes control access to API resources by determining user
privileges for different HTTP operations. They are applied at the view level,
enabling authentication and authorization to secure endpoints based on
predefined access rules.
"""

from rest_framework import permissions

__all__ = ['StaffWriteAuthenticatedRead']


class StaffWriteAuthenticatedRead(permissions.BasePermission):
    """Grant read-only access is granted to all authenticated users.

    Staff users retain all read/write permissions.
    """

    def has_permission(self, request, view) -> bool:
        """Return whether the request has permissions to access the requested resource"""

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_staff or request.user.is_superuser
