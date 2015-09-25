from django.conf.urls import include, url
from django.contrib import admin

from schools.urls import router as schools_router

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(schools_router.urls)),
]
