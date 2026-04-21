"""
Permisos a nivel de objeto para Evaluaciones.
Cumple con OWASP SbD - Domain 5: Access Control & Secure Communication
Cumple con LFPDPPP - Protección de datos personales
"""
from rest_framework import permissions
from apps.users.models import Usuarios


class IsManagerOrContraloriaOrSelf(permissions.BasePermission):
    """
    Permiso personalizado que garantiza:
    - Un empleado solo puede ver sus propias evaluaciones (GET)
    - Un Manager solo puede ver las evaluaciones de sus subordinados
    - Contraloria/Admin tiene acceso total
    
    Este permiso protege los datos personales de los empleados
    según LFPDPPP Art. 6 - Derecho a la protección de datos.
    """
    
    FULL_ACCESS_ROLES = ['administrador', 'contraloria']
    
    def has_object_permission(self, request, view, obj):
        http_method = request.method
        user = request.user
        
        user_rol = getattr(user, 'rol', None)
        rol_nombre = getattr(user_rol, 'nombre', '').lower() if user_rol else ''
        
        if rol_nombre in self.FULL_ACCESS_ROLES:
            return True
        
        if http_method in permissions.SAFE_METHODS:
            return self._can_read_evaluation(user, obj)
        
        return self._can_write_evaluation(user, obj, rol_nombre)
    
    def _can_read_evaluation(self, user, obj):
        if obj.evaluado_id == user.id:
            return True
        
        if obj.evaluado.manager_id == user.id:
            return True
        
        if obj.evaluador_id == user.id:
            return True
        
        user_rol = getattr(user, 'rol', None)
        rol_nombre = getattr(user_rol, 'nombre', '').lower() if user_rol else ''
        
        if rol_nombre in ['gerente', 'director']:
            if obj.evaluado.departamento_id == user.departamento_id:
                return True
        
        return False
    
    def _can_write_evaluation(self, user, obj, rol_nombre):
        if rol_nombre in self.FULL_ACCESS_ROLES:
            return True
        
        if obj.estado == 'DRAFT':
            return obj.evaluado_id == user.id
        
        if obj.estado == 'SUBMITTED':
            return obj.evaluador_id == user.id
        
        return False
