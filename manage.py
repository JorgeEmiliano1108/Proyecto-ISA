#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # ==============================================================
    # INICIO: SENSOR DE CONEXIÓN A SUPABASE (SISTEMA ISA)
    # ==============================================================
    # Solo verificamos en comandos clave para no saturar la terminal
    comandos_clave = ['runserver', 'migrate', 'inspectdb']
    
    if any(cmd in sys.argv for cmd in comandos_clave):
        try:
            import django
            django.setup()
            from django.db import connections
            from django.db.utils import OperationalError
            
            # Intentamos forzar el "ping" a la base de datos
            connections['default'].cursor()
            print("\n[SISTEMA ISA] - Conexión a Supabase (PostgreSQL) ¡ESTABLECIDA CON ÉXITO!\n")
            
        except OperationalError as e:
            print("\n[SISTEMA ISA] - ERROR FATAL: No se pudo conectar a Supabase.")
            print(f"Revisa tu archivo .env o tu conexión a internet.")
            print(f"Detalle técnico:\n{e}\n")
            sys.exit(1) # Detiene la ejecución inmediatamente
        except Exception:
            pass # Si es otro tipo de error de inicialización, dejamos que Django lo maneje
    # ==============================================================
    # FIN DEL SENSOR
    # ==============================================================

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()