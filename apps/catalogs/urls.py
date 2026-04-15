from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CatRolesViewSet,
    CatDepartamentosViewSet,
    CatPeriodosViewSet,
    CatCompetenciasViewSet
)

app_name = 'catalogs'

router = DefaultRouter()
router.register(r'roles', CatRolesViewSet)
router.register(r'departamentos', CatDepartamentosViewSet)
router.register(r'periodos', CatPeriodosViewSet)
router.register(r'competencias', CatCompetenciasViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
