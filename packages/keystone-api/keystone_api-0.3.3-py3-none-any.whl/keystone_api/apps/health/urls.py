"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'health'

router = DefaultRouter()
router.register('', HealthChecks, basename='health')

urlpatterns = router.urls
