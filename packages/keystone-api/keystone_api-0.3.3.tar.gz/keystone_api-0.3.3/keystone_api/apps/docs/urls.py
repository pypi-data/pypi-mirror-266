"""URL routing for the parent application"""

from django.urls import path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

app_name = 'docs'

urlpatterns = [
    path('openapi', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularRedocView.as_view(url_name='docs:schema'), name='redoc'),
]
