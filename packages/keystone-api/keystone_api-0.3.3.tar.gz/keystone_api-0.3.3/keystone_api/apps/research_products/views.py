"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets

from .models import *
from .serializers import *

__all__ = ['GrantViewSet', 'PublicationViewSet']


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """Manage metadata for research publications."""

    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    filterset_fields = '__all__'


class GrantViewSet(viewsets.ReadOnlyModelViewSet):
    """Track funding awards and grant information."""

    queryset = Grant.objects.all()
    serializer_class = GrantSerializer
    filterset_fields = '__all__'
