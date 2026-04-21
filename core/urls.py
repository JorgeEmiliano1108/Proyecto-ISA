from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/catalogs/', include('apps.catalogs.urls')),
    path('api/v1/evaluations/', include('apps.evaluations.urls')),
]