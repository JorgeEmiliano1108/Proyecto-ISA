from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import User, Group

BLOQUES_ISA = {
    'Catálogos': ['CatRoles', 'CatDepartamentos', 'CatPeriodos', 'CatCompetencias'],
    'Seguridad': ['Usuarios'],
    'Transaccional': ['Evaluaciones', 'CompetenciasDetalle', 'Objetivos'],
    'Auditoría': ['HistorialEstados', 'Aprobaciones', 'LogsSistema'],
    'Finanzas': ['Bonos']
}

class ISAAdminSite(admin.AdminSite):
    site_header = "SISTEMA ISA - Corporativo"
    site_title = "Panel de Control"
    index_title = "Módulos del Sistema"

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        
        # Buscamos nuestra app 'sistema_isa'
        app_isa = next((app for app in app_list if app['app_label'] == 'sistema_isa'), None)
        if not app_isa:
            return app_list

        nuevos_bloques = []
        modelos_dict = {m['object_name']: m for m in app_isa['models']}

        for nombre_bloque, nombres_modelos in BLOQUES_ISA.items():
            modelos_del_bloque = []
            for modelo in nombres_modelos:
                if modelo in modelos_dict:
                    modelos_del_bloque.append(modelos_dict[modelo])
            
            if modelos_del_bloque:
                nuevos_bloques.append({
                    'name': nombre_bloque,
                    'app_label': nombre_bloque.lower(),
                    'app_url': '', 
                    'has_module_perms': True,
                    'models': modelos_del_bloque
                })

        otras_apps = [app for app in app_list if app['app_label'] != 'sistema_isa']
        return otras_apps + nuevos_bloques

admin_site = ISAAdminSite(name='isa_admin')
admin_site.register(User)
admin_site.register(Group)

# Registramos los modelos de tu app
app = apps.get_app_config('sistema_isa')
for model_name, model in app.models.items():
    try:
        admin_site.register(model)
    except admin.sites.AlreadyRegistered:
        pass