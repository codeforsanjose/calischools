from rest_framework.routers import DefaultRouter

from .views import (
    CountyViewSet,
    DistrictViewSet,
    SchoolViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'counties', CountyViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'schools', SchoolViewSet)
