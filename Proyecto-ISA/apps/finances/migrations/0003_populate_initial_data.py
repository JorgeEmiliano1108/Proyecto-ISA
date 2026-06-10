"""
Migración para poblar datos iniciales de bonos desde el frontend hardcodeado.
"""
import uuid
from decimal import Decimal
from django.db import migrations
from django.utils import timezone
from django.conf import settings


def crear_programas_iniciales(apps, schema_editor):
    """Crea los programas de bono iniciales basados en datos del frontend."""
    BonoPrograma = apps.get_model('finances', 'BonoPrograma')
    BonoMetasVinculadas = apps.get_model('finances', 'BonoMetasVinculadas')
    
    # Programa 1: Multiplicador de Desempeño
    programa1 = BonoPrograma.objects.create(
        id=uuid.UUID('11111111-1111-1111-1111-111111111111'),
        nombre='Multiplicador de Desempeño',
        descripcion='Cálculo del 15% del salario base anual basado en el cumplimiento trimestral de OKRs estratégicos para el nivel ejecutivo.',
        tipo_calculo='porcentaje_salario',
        valor=Decimal('15.00'),
        presupuesto_limite=Decimal('1000000.00'),
        fecha_inicio=timezone.now().date().replace(month=1, day=1),
        fecha_fin=timezone.now().date().replace(month=12, day=31),
        estado='activo',
    )
    
    # Metas vinculadas al programa 1
    BonoMetasVinculadas.objects.bulk_create([
        BonoMetasVinculadas(
            programa=programa1,
            titulo="Disponibilidad de Servidores",
            meta="99.9%",
            actual="99.5%",
            icono="🖥️"
        ),
        BonoMetasVinculadas(
            programa=programa1,
            titulo="Certificación Cloud",
            meta="1",
            actual="1",
            icono="📜"
        ),
        BonoMetasVinculadas(
            programa=programa1,
            titulo="Feedback de Equipo",
            meta="4.5/5",
            actual="4.2/5",
            icono="🤝"
        ),
    ])
    
    # Programa 2: Hito de Retención
    programa2 = BonoPrograma.objects.create(
        id=uuid.UUID('22222222-2222-2222-2222-222222222222'),
        nombre='Hito de Retención',
        descripcion='Monto fijo de $25,000 pagados al completar 36 meses de antigüedad ininterrumpida como estrategia de retención de talento clave.',
        tipo_calculo='monto_fijo',
        valor=Decimal('25000.00'),
        presupuesto_limite=Decimal('500000.00'),
        fecha_inicio=timezone.now().date().replace(month=7, day=1),
        fecha_fin=timezone.now().date().replace(month=9, day=30),
        estado='planeado',
    )
    
    # No hay metas vinculadas para el programa 2 por ahora


def crear_empleados_iniciales(apps, schema_editor):
    """Crea las asignaciones de empleados a programas basadas en datos del frontend."""
    BonoEmpleado = apps.get_model('finances', 'BonoEmpleado')
    BonoPrograma = apps.get_model('finances', 'BonoPrograma')
    Usuarios = apps.get_model('users', 'Usuarios')
    
    # Obtener programas
    try:
        programa1 = BonoPrograma.objects.get(nombre='Multiplicador de Desempeño')
        programa2 = BonoPrograma.objects.get(nombre='Hito de Retención')
    except BonoPrograma.DoesNotExist:
        return
    
    # Obtener usuarios (usar los que existen en la BD)
    usuarios_map = {}
    for u in Usuarios.objects.all():
        usuarios_map[u.username] = u
    
    # Datos basados en usuarios reales de la BD
    # mapeamos usuarios existentes a programas
    empleados_data = [
        {
            'username': 'admin.admin',  # Jorge Yael Padua Nava - Director
            'programa': 'Multiplicador de Desempeño',
            'salario_base': Decimal('283333.33'),
            'objetivo': Decimal('92.0'),
            'estado': 'en_progreso',
        },
        {
            'username': 'maria.garcia',  # María García López
            'programa': 'Hito de Retención',
            'salario_base': Decimal('25000.00'),
            'objetivo': Decimal('60.0'),
            'estado': 'pendiente',
        },
        {
            'username': 'ana.martinez',  # Ana Martínez Rodríguez
            'programa': 'Multiplicador de Desempeño',
            'salario_base': Decimal('182000.00'),
            'objetivo': Decimal('45.0'),
            'estado': 'en_progreso',
        },
    ]
    
    for emp_data in empleados_data:
        usuario = Usuarios.objects.filter(username=emp_data['username']).first()
        if not usuario:
            continue
            
        programa_nombre = emp_data['programa']
        programa = BonoPrograma.objects.filter(nombre=programa_nombre).first()
        if not programa:
            continue
        
        BonoEmpleado.objects.get_or_create(
            programa=programa,
            empleado=usuario,
            defaults={
                'salario_base': emp_data['salario_base'],
                'objetivo': emp_data['objetivo'],
                'estado': emp_data['estado'],
            }
        )


def crear_pagos_iniciales(apps, schema_editor):
    """Crea pagos iniciales basados en datos del frontend usuario/bonos."""
    BonoPago = apps.get_model('finances', 'BonoPago')
    BonoEmpleado = apps.get_model('finances', 'BonoEmpleado')
    Usuarios = apps.get_model('users', 'Usuarios')
    
    # Obtener usuario maria.garcia que tiene historial en usuario/bonos/bonos.js
    usuario = Usuarios.objects.filter(username='maria.garcia').first()
    if not usuario:
        return
    
    # Buscar asignaciones de este usuario
    asignaciones = BonoEmpleado.objects.filter(empleado=usuario)
    for asignacion in asignaciones:
        BonoPago.objects.get_or_create(
            empleado=usuario,
            programa=asignacion.programa,
            periodo='Q2 2023',
            defaults={
                'empleado_asignado': asignacion,
                'monto': Decimal('10200.00'),
                'periodo': 'Q2 2023',
                'fecha_pago': timezone.now().date().replace(month=7, day=15),
                'estado': 'pagado',
            }
        )
        BonoPago.objects.get_or_create(
            empleado=usuario,
            programa=asignacion.programa,
            periodo='Q1 2023',
            defaults={
                'empleado_asignado': asignacion,
                'monto': Decimal('9800.00'),
                'periodo': 'Q1 2023',
                'fecha_pago': timezone.now().date().replace(month=4, day=15),
                'estado': 'pagado',
            }
        )
        BonoPago.objects.get_or_create(
            empleado=usuario,
            programa=asignacion.programa,
            periodo='Q1 2023',
            defaults={
                'empleado_asignado': asignacion,
                'monto': Decimal('9800.00'),
                'periodo': 'Q1 2023',
                'fecha_pago': timezone.now().date().replace(month=4, day=15),
                'estado': 'pagado',
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0002_bonoempleado_bonometasvinculadas_bonopago_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_programas_iniciales, migrations.RunPython.noop),
        migrations.RunPython(crear_empleados_iniciales, migrations.RunPython.noop),
        migrations.RunPython(crear_pagos_iniciales, migrations.RunPython.noop),
    ]