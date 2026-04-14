from django.apps import AppConfig

class CatalogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalogs' # Nombre completo para que Django lo encuentre
    verbose_name = 'Catálogos del Sistema'