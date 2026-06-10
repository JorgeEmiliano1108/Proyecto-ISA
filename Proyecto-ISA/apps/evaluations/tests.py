"""
Tests para Evaluation Core Service.
Cumple con OWASP SbD - Verificación de seguridad.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.evaluations.models import Evaluaciones
from apps.users.models import Usuarios
from apps.catalogs.models import CatRoles, CatDepartamentos, CatPeriodos


class EvaluacionesPermissionsTestCase(TestCase):
    """Tests de seguridad de permisos."""

    def setUp(self):
        self.client = APIClient()

        self.rol_empleado = CatRoles.objects.create(nombre='Empleado', nivel_aprobacion=4)
        self.rol_manager = CatRoles.objects.create(nombre='Gerente', nivel_aprobacion=3)
        self.rol_admin = CatRoles.objects.create(nombre='Administrador', nivel_aprobacion=1)

        self.depto = CatDepartamentos.objects.create(nombre='Sistemas')
        self.periodo = CatPeriodos.objects.create(nombre='2025')

        self.empleado = Usuarios.objects.create(
            username='empleado_test',
            nombre_completo='Juan Perez',
            password='pbkdf2_sha256$test$hash',
            rol=self.rol_empleado,
            departamento=self.depto
        )

        self.manager = Usuarios.objects.create(
            username='manager_test',
            nombre_completo='Maria Garcia',
            password='pbkdf2_sha256$test$hash',
            rol=self.rol_manager,
            departamento=self.depto
        )

        self.empleado.manager = self.manager
        self.empleado.save()

        self.evaluacion = Evaluaciones.objects.create(
            evaluado=self.empleado,
            evaluador=self.manager,
            periodo=self.periodo,
            estado='DRAFT'
        )

    def test_empleado_puede_ver_su_propia_evaluacion(self):
        """Un empleado puede ver SU PROPIA evaluación."""
        self.client.force_authenticate(user=self.empleado)
        response = self.client.get(f'/api/v1/evaluations/{self.evaluacion.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empleado_no_puede_acceder_evaluacion_ajena(self):
        """Un empleado no puede ver evaluaciones de otros empleados."""
        otro_empleado = Usuarios.objects.create(
            username='otro_empleado',
            nombre_completo='Pedro Lopez',
            password='pbkdf2_sha256$test$hash',
            rol=self.rol_empleado,
            departamento=self.depto
        )
        otra_evaluacion = Evaluaciones.objects.create(
            evaluado=otro_empleado,
            evaluador=self.manager,
            periodo=self.periodo,
            estado='DRAFT'
        )

        self.client.force_authenticate(user=self.empleado)
        response = self.client.get(f'/api/v1/evaluations/{otra_evaluacion.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_puede_ver_evaluacion_de_subordinado(self):
        """Un manager puede ver las evaluaciones de sus subordinados."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/v1/evaluations/{self.evaluacion.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EvaluacionesStateMachineTestCase(TestCase):
    """Tests de la máquina de estados."""

    def setUp(self):
        self.client = APIClient()

        self.rol_empleado = CatRoles.objects.create(nombre='Empleado', nivel_aprobacion=4)
        self.rol_manager = CatRoles.objects.create(nombre='Gerente', nivel_aprobacion=3)
        self.depto = CatDepartamentos.objects.create(nombre='Sistemas')
        self.periodo = CatPeriodos.objects.create(nombre='2025')

        self.empleado = Usuarios.objects.create(
            username='empleado_test',
            nombre_completo='Juan Perez',
            password='pbkdf2_sha256$test$hash',
            rol=self.rol_empleado,
            departamento=self.depto
        )

        self.manager = Usuarios.objects.create(
            username='manager_test',
            nombre_completo='Maria Garcia',
            password='pbkdf2_sha256$test$hash',
            rol=self.rol_manager,
            departamento=self.depto
        )

        self.evaluacion = Evaluaciones.objects.create(
            evaluado=self.empleado,
            evaluador=self.manager,
            periodo=self.periodo,
            estado='DRAFT'
        )

    def test_submit_exitoso(self):
        """Test: Transición DRAFT -> SUBMITTED exitosa."""
        self.client.force_authenticate(user=self.empleado)
        response = self.client.post(f'/api/v1/evaluations/{self.evaluacion.id}/submit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, 'SUBMITTED')

    def test_estado_protegido_no_editable_via_put(self):
        """El campo estado no puede modificarse directamente via PUT/PATCH."""
        self.client.force_authenticate(user=self.empleado)
        response = self.client.patch(
            f'/api/v1/evaluations/{self.evaluacion.id}/',
            {'estado': 'APPROVED'},
            format='json'
        )
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, 'DRAFT')

    def test_reject_sin_comentario_falla(self):
        """Test: /reject/ sin comentario devuelve 400."""
        self.evaluacion.estado = 'PENDING_APPROVAL'
        self.evaluacion.save()

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/v1/evaluations/{self.evaluacion.id}/reject/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_comentario_corto_falla(self):
        """Test: /reject/ con comentario < 10 caracteres devuelve 400."""
        self.evaluacion.estado = 'PENDING_APPROVAL'
        self.evaluacion.save()

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/v1/evaluations/{self.evaluacion.id}/reject/',
            {'comentario': 'corto'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_con_comentario_valido_exitoso(self):
        """Test: /reject/ con comentario válido pasa a DRAFT."""
        self.evaluacion.estado = 'PENDING_APPROVAL'
        self.evaluacion.save()

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/v1/evaluations/{self.evaluacion.id}/reject/',
            {'comentario': 'El desempeño no cumple con los objetivos'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, 'DRAFT')

    def test_flujo_completo_happy_path(self):
        """Test: Flujo completo DRAFT -> SUBMITTED -> APPROVED"""
        # Paso 1: Empleado envía evaluación
        self.client.force_authenticate(user=self.empleado)
        response = self.client.post(f'/api/v1/evaluations/{self.evaluacion.id}/submit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Paso 2: Manager aprueba
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f'/api/v1/evaluations/{self.evaluacion.id}/approve/',
            {'comentario': 'Excelente trabajo'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, 'APPROVED')
