"""
Data Migration para crear grupos del sistema ISA
Ejecutar: python manage.py migrate
"""
from django.db import migrations
from django.contrib.auth.models import Group


def create_groups(apps, schema_editor):
    """Crear grupos del sistema"""
    grupos = ['admin', 'Director', 'Gerente', 'Coordinador', 'Contraloria']
    created = []
    for nombre in grupos:
        group, was_created = Group.objects.get_or_create(name=nombre)
        if was_created:
            created.append(nombre)
    if created:
        print(f"Grupos creados: {', '.join(created)}")
    else:
        print("Grupos ya existen")


def remove_groups(apps, schema_editor):
    """Eliminar grupos del sistema"""
    grupos = ['admin', 'Director', 'Gerente', 'Coordinador', 'Contraloria']
    deleted = Group.objects.filter(name__in=grupos).delete()
    print(f"Grupos eliminados: {deleted[0]}")


class Migration(migrations.Migration):
    dependencies = [
        ('evaluations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]