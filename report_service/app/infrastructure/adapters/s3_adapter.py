"""app/infrastructure/adapters/s3_adapter.py

Adaptador de Almacenamiento en Nube (S3 / MinIO).
Implementa CloudStoragePort para subir, firmar y eliminar reportes PDF de manera efímera,
cumpliendo con la Arquitectura Hexagonal y la LFPDPPP (Destrucción Segura).
"""

import logging
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.application.ports.output import CloudStoragePort

logger = logging.getLogger("ms_reports.s3_adapter")

class S3Adapter(CloudStoragePort):
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET
        
        try:
            # Inicializamos el cliente boto3 apuntando a MinIO local o AWS S3
            # region_name es requerido por la librería boto3 aunque usemos MinIO
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name='us-east-1' 
            )
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"Error crítico al inicializar el cliente S3/MinIO: {e}")

    def _ensure_bucket_exists(self):
        """Verifica si el bucket existe, y si no, lo crea automáticamente al arrancar."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            # Si el error es 404, el bucket no existe, procedemos a crearlo
            if error_code == '404':
                logger.info(f"El bucket '{self.bucket_name}' no existe. Creándolo...")
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                logger.error(f"Error de permisos o red al verificar el bucket S3: {e}")

    # =========================================================================
    # IMPLEMENTACIÓN DEL PUERTO DE ALMACENAMIENTO (CloudStoragePort)
    # =========================================================================
    def upload_pdf(self, file_bytes: bytes, file_name: str) -> None:
        """Sube el archivo PDF en formato binario puro directamente a la nube."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_bytes,
                ContentType='application/pdf'
            )
            logger.info(f"Archivo {file_name} subido exitosamente a S3.")
        except Exception as e:
            logger.error(f"Fallo al subir {file_name} a S3: {e}")
            raise

    def generate_presigned_url(self, file_name: str, expires_in_sec: int = 300) -> str:
        """
        Genera una URL segura y temporal (Pre-signed URL).
        Por defecto, la URL caducará en 5 minutos (300 segundos).
        """
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_name
                },
                ExpiresIn=expires_in_sec
            )
            return url
        except Exception as e:
            logger.error(f"Error generando Presigned URL para {file_name}: {e}")
            raise

    def delete_pdf(self, file_name: str) -> None:
        """
        Elimina permanentemente el documento del bucket.
        Fundamental para cumplir con el principio de minimización de la LFPDPPP.
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            logger.info(f"Archivo {file_name} purgado exitosamente de S3 (LFPDPPP).")
        except Exception as e:
            logger.error(f"Error al intentar eliminar {file_name} de S3: {e}")
            raise