"""app/domain/sanitizer.py
Clase pura de dominio para aplicar reglas de enmascaramiento y anonimización
para cumplir con el principio de minimización de la LFPDPPP (México).
"""
import re
from typing import Any, Dict

class DataSanitizer:
    
    # --- PATRONES REGEX PARA PII MEXICANO (ME-04) ---
    # RFC: 3 o 4 letras, 6 números (AAMMDD), y 3 caracteres alfanuméricos (homoclave)
    RFC_PATTERN = re.compile(r'\b[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}\b', re.IGNORECASE)
    
    # CURP: 4 letras, 6 números, H/M, 5 letras de estado/consonantes, 2 alfanuméricos
    CURP_PATTERN = re.compile(r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d\b', re.IGNORECASE)
    
    # NSS (IMSS): 11 dígitos, a veces separados por guiones o espacios
    NSS_PATTERN = re.compile(r'\b\d{2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{1}\b')

    @staticmethod
    def mask_name(name: str) -> str:
        """Enmascara nombres: 'Juan Perez' -> 'J*** P****'"""
        if not name:
            return ""
        words = name.split()
        masked_words = [w[0] + "*" * (len(w) - 1) if len(w) > 1 else w for w in words]
        return " ".join(masked_words)

    @staticmethod
    def mask_email(email: str) -> str:
        """Enmascara correos: 'jperez@isacorporativo.com' -> 'j****@isacorporativo.com'"""
        if not email or "@" not in email:
            return email
        local, domain = email.split("@")
        if len(local) > 2:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        else:
            masked_local = "***"
        return f"{masked_local}@{domain}"

    @classmethod
    def mask_free_text(cls, text: str) -> str:
        """
        Escanea un bloque de texto libre y ofusca claves de identificación oficiales.
        """
        if not text:
            return ""
        
        # Sustituimos las coincidencias con etiquetas genéricas
        text = cls.CURP_PATTERN.sub("[CURP OCULTA]", text)
        text = cls.RFC_PATTERN.sub("[RFC OCULTO]", text)
        text = cls.NSS_PATTERN.sub("[NSS OCULTO]", text)
        
        return text

    @classmethod
    def sanitize_evaluation_payload(cls, raw_data: dict) -> Dict[str, Any]:
        """
        Recorre el diccionario de la evaluación y enmascara los campos sensibles
        estructurados y de texto libre antes de que la IA (Ollama) los procese.
        """
        sanitized = raw_data.copy()
        
        # 1. Enmascarar información estructurada (Nombres)
        if "evaluado" in sanitized and isinstance(sanitized["evaluado"], dict):
            sanitized["evaluado"]["username"] = cls.mask_name(sanitized["evaluado"].get("username", ""))
            
        if "evaluador" in sanitized and isinstance(sanitized["evaluador"], dict):
            sanitized["evaluador"]["username"] = cls.mask_name(sanitized["evaluador"].get("username", ""))
            
        # 2. Enmascarar texto libre (Cabecera de la evaluación)
        text_fields = ["logros_previos", "comentarios_evaluador", "comentarios_evaluado"]
        for field in text_fields:
            if sanitized.get(field):
                sanitized[field] = cls.mask_free_text(sanitized[field])
                
        # 3. Enmascarar texto libre anidado (Comentarios de cada competencia)
        if "competencias" in sanitized and isinstance(sanitized["competencias"], list):
            for comp in sanitized["competencias"]:
                if isinstance(comp, dict) and comp.get("comentario"):
                    comp["comentario"] = cls.mask_free_text(comp["comentario"])
        
        return sanitized