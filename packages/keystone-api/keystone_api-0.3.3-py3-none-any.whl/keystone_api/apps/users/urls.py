"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'users'

router = DefaultRouter()
router.register(r'researchgroups', ResearchGroupViewSet, basename='ResearchGroup')
router.register(r'users', UserViewSet, basename='User')

urlpatterns = router.urls
