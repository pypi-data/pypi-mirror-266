"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'logging'

router = DefaultRouter()
router.register('apps', AppLogViewSet)
router.register('requests', RequestLogViewSet)

urlpatterns = router.urls
