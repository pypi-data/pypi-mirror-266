"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import *
from .permissions import *
from .serializers import *

__all__ = [
    'AllocationViewSet',
    'AllocationRequestViewSet',
    'AllocationRequestReviewViewSet',
    'ClusterViewSet'
]


class AllocationViewSet(viewsets.ModelViewSet):
    """Manage allocations for user research groups."""

    permission_classes = [permissions.IsAuthenticated, StaffWriteGroupRead]
    serializer_class = AllocationSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of allocations for the currently authenticated user"""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return Allocation.objects.all()

        return Allocation.objects.affiliated_with_user(self.request.user).all()


class AllocationRequestViewSet(viewsets.ModelViewSet):
    """Manage allocation requests submitted by user research groups."""

    permission_classes = [permissions.IsAuthenticated, GroupAdminCreateGroupRead]
    serializer_class = AllocationRequestSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[AllocationRequest]:
        """Return a list of allocation requests for the currently authenticated user"""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return AllocationRequest.objects.all()

        return AllocationRequest.objects.affiliated_with_user(self.request.user).all()


class AllocationRequestReviewViewSet(viewsets.ModelViewSet):
    """Manage reviews of allocation request submitted by administrators."""

    permission_classes = [permissions.IsAuthenticated, StaffWriteGroupRead]
    serializer_class = AllocationRequestReviewSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of allocation reviews for the currently authenticated user"""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return AllocationRequestReview.objects.all()

        return AllocationRequestReview.objects.affiliated_with_user(self.request.user).all()

    def create(self, request, *args, **kwargs) -> Response:
        """Create a new `AllocationRequestReview` object"""

        data = request.data.copy()
        data.setdefault('reviewer', request.user.pk)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ClusterViewSet(viewsets.ModelViewSet):
    """Configuration settings for managed Slurm clusters."""

    queryset = Cluster.objects.all()
    permission_classes = [permissions.IsAuthenticated, StaffWriteAuthenticatedRead]
    serializer_class = ClusterSerializer
    filterset_fields = '__all__'
