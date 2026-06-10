"""
Views for Finances app - Bonos integration.
Proxies requests to bonus_service microservice.
"""
import requests
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    CalculoLogroRequestSerializer,
    CalculoLogroBatchRequestSerializer,
    CalculoLogroReportResponseSerializer,
    CalculosListQueryParamsSerializer,
    PaginatedCalculosResponseSerializer,
)

logger = logging.getLogger(__name__)


class BonusServiceProxyMixin:
    """Mixin para llamar al microservicio de bonos."""
    
    BASE_URL = getattr(settings, 'BONUS_SERVICE_URL', 'http://bonus_api:8004')
    INTERNAL_API_KEY = getattr(settings, 'INTERNAL_API_KEY', 'isa_internal_key_2026')

    def _get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'X-Internal-Api-Key': getattr(settings, 'INTERNAL_API_KEY', 'isa_internal_key_2026'),
        }
        return headers

    def _handle_response(self, response):
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = {'detail': response.text}
            from rest_framework.response import Response
            return Response(error_data, status=response.status_code)
        return Response(response.json(), status=response.status_code)


class CalculateBonoView(APIView):
    """Proxy para cálculo individual de logro."""
    
    def post(self, request):
        from .serializers import CalculoLogroRequestSerializer
        
        from rest_framework import serializers
        from django.conf import settings
        
        serializer = CalculoLogroRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            response = requests.post(
                f"{settings.BONUS_SERVICE_URL}/api/v1/bonus/calculate/",
                json=serializer.validated_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-Internal-Api-Key': settings.INTERNAL_API_KEY,
                },
                timeout=10
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {'detail': response.text}
                return Response(error_data, status=response.status_code)
            
            return Response(response.json(), status=response.status_code)
            
        except requests.exceptions.Timeout:
            return Response(
                {'detail': 'Timeout al conectar con servicio de bonos'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'detail': 'No se pudo conectar al servicio de bonos'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Error en calculate_bono: {e}")
            return Response(
                {'detail': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalculateBonoBatchView(APIView):
    """Proxy para cálculo batch de logros."""
    
    def post(self, request):
        from rest_framework import status
        import requests
        from django.conf import settings
        
        try:
            response = requests.post(
                f"{settings.BONUS_SERVICE_URL}/api/v1/bonus/calculate/batch/",
                json=request.data,
                headers={
                    'Content-Type': 'application/json',
                    'X-Internal-Api-Key': settings.INTERNAL_API_KEY,
                },
                timeout=30
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {'detail': response.text}
                return Response(error_data, status=response.status_code)
            
            return Response(response.json(), status=response.status_code)
            
        except requests.exceptions.Timeout:
            return Response(
                {'detail': 'Timeout al conectar con servicio de bonos'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'detail': 'No se pudo conectar al servicio de bonos'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Error en batch calculate: {e}")
            return Response(
                {'detail': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BonoReportView(APIView):
    """Proxy para reporte de bonos por periodo."""
    
    def get(self, request, periodo_id):
        import requests
        from django.conf import settings
        from rest_framework import status
        
        try:
            response = requests.get(
                f"{settings.BONUS_SERVICE_URL}/api/v1/bonus/report/{periodo_id}/",
                headers={
                    'Content-Type': 'application/json',
                    'X-Internal-Api-Key': settings.INTERNAL_API_KEY,
                },
                timeout=10
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {'detail': response.text}
                return Response(error_data, status=response.status_code)
            
            return Response(response.json(), status=response.status_code)
            
        except requests.exceptions.Timeout:
            return Response(
                {'detail': 'Timeout al conectar con servicio de bonos'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'detail': 'No se pudo conectar al servicio de bonos'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Error en bono report: {e}")
            return Response(
                {'detail': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BonoListView(APIView):
    """Lista paginada de cálculos de bonos con filtros."""
    
    def get(self, request):
        import requests
        from django.conf import settings
        from rest_framework import status
        
        # Build query params
        params = {}
        for key, value in request.query_params.items():
            if value:
                params[key] = value
        
        try:
            response = requests.get(
                f"{settings.BONUS_SERVICE_URL}/api/v1/bonus/calculos/",
                params=params,
                headers={
                    'Content-Type': 'application/json',
                    'X-Internal-Api-Key': settings.INTERNAL_API_KEY,
                },
                timeout=10
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {'detail': response.text}
                return Response(error_data, status=response.status_code)
            
            return Response(response.json(), status=response.status_code)
            
        except requests.exceptions.Timeout:
            return Response(
                {'detail': 'Timeout al conectar con servicio de bonos'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'detail': 'No se pudo conectar al servicio de bonos'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Error en listado de bonos: {e}")
            return Response(
                {'detail': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )