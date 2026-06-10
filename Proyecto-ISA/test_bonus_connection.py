#!/usr/bin/env python
"""
Script de prueba para validar la conexión Django → Bonus Service.
Ejecutar desde la raíz del proyecto: python test_bonus_connection.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import requests
from django.conf import settings

def obtener_token_bonus_service():
    """Obtiene un token JWT del endpoint de login de bonus_service."""
    url = f"{settings.BONUS_SERVICE_URL}/api/v1/auth/login"
    payload = {
        "username": "system_django",
        "password": "system_django"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        print(f"    ✗ Error obteniendo token: HTTP {response.status_code}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    return None

def test_bonus_service_connection():
    print("=" * 70)
    print("PRUEBA DE CONEXIÓN: Django → Bonus Service")
    print("=" * 70)
    
    bonus_url = settings.BONUS_SERVICE_URL
    
    print(f"\n[1] Configuración:")
    print(f"    BONUS_SERVICE_URL: {bonus_url}")
    
    print(f"\n[2] Obteniendo token de autenticación...")
    token = obtener_token_bonus_service()
    if token:
        print(f"    ✓ Token obtenido: {token[:20]}...")
    else:
        print(f"    ✗ No se pudo obtener token")
        token = "no-token"
    
    print(f"\n[3] Probando cálculo de logro (calificación 4.0)...")
    payload = {
        "evaluacion_id": "12345678-1234-1234-1234-123456789012",
        "calificacion_global": 4.0
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            f"{bonus_url}/api/v1/bonus/calculate",
            json=payload,
            headers=headers,
            timeout=5
        )
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"    ✓ Éxito!")
            print(f"    Evaluación ID: {data.get('evaluacion_id')}")
            print(f"    Calificación: {data.get('calificacion_global')}")
            print(f"    Porcentaje de Logro: {data.get('porcentaje_logro')}%")
            
            expected_percentage = 4.0 * 20.0
            actual_percentage = data.get('porcentaje_logro')
            
            if abs(actual_percentage - expected_percentage) < 0.01:
                print(f"    ✓ Cálculo correcto: 4.0 × 20 = {actual_percentage}%")
            else:
                print(f"    ✗ Cálculo incorrecto: esperado {expected_percentage}%, obtenido {actual_percentage}%")
        else:
            print(f"    ✗ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"    ✗ Timeout: Bonus Service no respondió en 5s")
    except requests.exceptions.ConnectionError as e:
        print(f"    ✗ Conexión fallida: {e}")
    except Exception as e:
        print(f"    ✗ Error inesperado: {type(e).__name__} - {e}")
    
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70)

if __name__ == '__main__':
    test_bonus_service_connection()