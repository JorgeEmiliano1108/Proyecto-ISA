"""app/core/rbac.py

Gestor Centralizado de Control de Acceso Basado en Roles (RBAC).
Lee las políticas desde permissions.yaml para evitar roles hardcodeados en el código.
"""
import os
import yaml
import logging

logger = logging.getLogger("ms_reports.rbac")

class RBACManager:
    def __init__(self, policy_path: str = "app/core/permissions.yaml"):
        self.policies = {}
        self._load_policies(policy_path)

    def _load_policies(self, path: str):
        if not os.path.exists(path):
            logger.warning(f"Archivo de políticas RBAC no encontrado en {path}. Usando default vacío.")
            return
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.policies = data.get("roles", {})
            logger.info("Políticas RBAC cargadas exitosamente.")
        except Exception as e:
            logger.error(f"Fallo al parsear el archivo RBAC YAML: {e}")

    def has_permission(self, role: str, action: str) -> bool:
        """Verifica si un rol específico tiene concedido un permiso (action)."""
        # Si el rol no existe en el YAML, devuelve una lista vacía por defecto
        role_permissions = self.policies.get(role, [])
        return action in role_permissions

# Instancia global (Singleton) para ser importada en el resto de la aplicación
rbac_manager = RBACManager()