"""
Script para crear grupos y usuarios de prueba iniciales
Ejecutar: python manage.py shell < create_initial_users.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.db import transaction

def create_groups():
    """Crear grupos del sistema"""
    grupos = ['admin', 'Director', 'Gerente', 'Coordinador', 'Contraloria']
    
    for nombre in grupos:
        grupo, created = Group.objects.get_or_create(name=nombre)
        if created:
            print(f"✓ Grupo creado: {nombre}")
        else:
            print(f"- Grupo ya existe: {nombre}")
    
    return Group.objects.all()

def create_users():
    """Crear usuarios de prueba"""
    usuarios_data = [
        {
            'username': 'admin',
            'password': 'ISA2026_admin',
            'first_name': 'Admin',
            'last_name': 'ISA',
            'email': 'admin@isa.local',
            'groups': ['admin'],
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'director1',
            'password': 'ISA2026_director1',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'email': 'director1@isa.local',
            'groups': ['Director'],
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'gerente1',
            'password': 'ISA2026_gerente1',
            'first_name': 'María',
            'last_name': 'López',
            'email': 'gerente1@isa.local',
            'groups': ['Gerente'],
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'coordinador1',
            'password': 'ISA2026_coordinador1',
            'first_name': 'José',
            'last_name': 'Ramírez',
            'email': 'coordinador1@isa.local',
            'groups': ['Coordinador'],
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'contralor1',
            'password': 'ISA2026_contralor1',
            'first_name': 'Ana',
            'last_name': 'García',
            'email': 'contralor1@isa.local',
            'groups': ['Contraloria'],
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    created_users = []
    for data in usuarios_data:
        username = data.pop('username')
        password = data.pop('password')
        groups = data.pop('groups')
        
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            user.set_password(password)
            for key, value in data.items():
                setattr(user, key, value)
            user.save()
            print(f"✓ Usuario creado: {username}")
        else:
            print(f"- Usuario ya existe: {username}")
        
        for group_name in groups:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                print(f"  × Grupo no encontrado: {group_name}")
        
        created_users.append(user)
    
    return created_users

@transaction.atomic
def main():
    print("=" * 50)
    print("Creando grupos y usuarios de prueba")
    print("=" * 50)
    
    groups = create_groups()
    print()
    users = create_users()
    print()
    print("=" * 50)
    print(f"✓ Proceso completado: {len(users)} usuarios creados")
    print("=" * 50)

if __name__ == '__main__':
    main()