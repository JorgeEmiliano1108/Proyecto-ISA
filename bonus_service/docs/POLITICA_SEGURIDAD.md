# POLÍTICA DE SEGURIDAD Y PROTECCIÓN DE DATOS PERSONALES

**Microservicio: bonus_service**  
**Versión:** 1.0.0  
**Fecha de elaboración:** 15 de abril de 2026  
**Autor:** Cruz Felipe (Cruz Bravo) – Responsable Técnico ISA Corporativo  
**Clasificación:** Confidencial (Uso interno y auditoría INAI)

---

## 1. Objetivo
Establecer las medidas de seguridad administrativas, técnicas y físicas que garantizan la protección de los datos personales tratados en el microservicio `bonus_service`, conforme a la **Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)** publicada el 20 de marzo de 2025, especialmente los artículos 18 al 27.

---

## 2. Ámbito de aplicación
Esta política aplica a:
- Todos los datos personales y datos sensibles almacenados o procesados por `bonus_service`.
- La base de datos `bonos` (escritura).
- La base de datos `evaluaciones` (solo lectura).
- Los flujos de cálculo individual y batch (Celery).
- Los eventos enviados a Redis (`audit.events`).

---

## 3. Datos personales y sensibles tratados

| Dato                          | Tipo          | Sensibilidad | Tratamiento                  |
|-------------------------------|---------------|--------------|------------------------------|
| salario_base_snapshot        | Financiero    | Alta         | Cifrado en reposo (AES-256) |
| monto_final_bono              | Financiero    | Alta         | Cifrado en reposo (AES-256) |
| evaluacion_id                 | Identificador | Media        | En claro                     |
| performance_index             | Calculado     | Media        | En claro                     |
| impacto_ebitda_logrado        | Calculado     | Media        | En claro                     |
| calculado_por (user_id)       | Identificador | Media        | En claro (trazabilidad)      |

---

## 4. Medidas de Seguridad (LFPDPPP Art. 18-19)

### 4.1 Medidas Administrativas
- Documento de Seguridad vigente (este documento).
- Roles y responsabilidades definidos:
  - Responsable: Área de Finanzas / Sistemas
  - Encargado: Desarrollador del microservicio
  - Delegado de Protección de Datos: Cruz Felipe
- Capacitación anual en protección de datos al equipo técnico.
- Registro de Tratamientos de Datos Personales actualizado.

### 4.2 Medidas Técnicas
- **Cifrado en reposo**: Todos los campos sensibles (`salario_base_snapshot` y `monto_final_bono`) se cifran con **Fernet (AES-256)** antes de persistir en PostgreSQL/Supabase.
- **Cifrado en tránsito**: Todas las comunicaciones usan TLS 1.3 (HTTPS, PostgreSQL SSL, Redis TLS).
- **JWT**: Solo validación (no generación). Token emitido por Django con caducidad de 15 minutos.
- **Claves secretas**: Gestionadas mediante Docker Secrets / Vault (nunca hardcodeadas).
- **Rate limiting**: Pendiente de implementación en capa API.
- **Idempotencia**: Implementada en cálculos de bono.

### 4.3 Medidas Físicas
- Infraestructura en Supabase (cloud) con controles de acceso físico gestionados por el proveedor.
- Acceso al código fuente restringido vía GitHub + 2FA y branch protection.

---

## 5. Gestión de Incidentes y Brechas de Seguridad (Art. 26-27)
- Toda brecha de seguridad será notificada al INAI en un plazo máximo de **72 horas**.
- Se mantiene un **Registro de Incidentes** con:
  - Fecha y hora de detección
  - Descripción de la brecha
  - Datos afectados
  - Medidas correctivas tomadas
- Canal de notificación: Evento Redis `breach.detected` → `audit_service`.

---

## 6. Retención y Borrado de Datos
- Los registros en la tabla `bonos` se conservan durante **5 años** (cumplimiento fiscal y laboral).
- Después de 5 años se aplica borrado seguro (DELETE + vacuum).
- Solicitudes de derecho de cancelación serán atendidas en máximo 10 días hábiles.

---

## 7. Control de Acceso
- Acceso basado en roles (`require_role`).
- Principio de **mínimo privilegio**: solo lectura en `evaluaciones`.
- Auditoría de accesos vía eventos Redis.

---

## 8. Revisión y Actualización
- Esta política se revisa **anualmente** o cuando haya cambios significativos en el microservicio.
- Próxima revisión: Abril 2027.

---

**Aprobado por:**  
Cruz Felipe – Arquitecto de Software  
Fecha: 15 de abril de 2026

---

**Nota para auditoría INAI:**  
Este documento forma parte del **Expediente de Medidas de Seguridad** del Responsable. Se encuentra disponible en la carpeta `/docs/` del repositorio del proyecto.
