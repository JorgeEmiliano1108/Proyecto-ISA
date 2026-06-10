/**
 * Servicio de Bonos - Capa de servicio para comunicación con API Django.
 * Reemplaza los mocks hardcodeados por llamadas reales a la API.
 */
import { apiFetch } from '../../components/layout/layout.js';

export const BonosService = {
    /**
     * Obtiene resumen de programas de bonos (para admin)
     * GET /api/v1/finances/bonos/report/{periodo_id}/
     */
    async getResumenProgramas(periodoId = 1) {
        const res = await apiFetch(`/finances/bonos/report/${periodoId}/`);
        if (!res.ok) throw new Error('Error al obtener resumen de programas');
        return res.json();
    },

    /**
     * Obtiene asignación de empleados con paginación
     * GET /api/v1/finances/bonos/calculos/
     */
    async getAsignacionEmpleados(params = {}) {
        const query = new URLSearchParams({
            page: params.page || 1,
            page_size: params.page_size || 20,
            ...params
        }).toString();
        
        const res = await apiFetch(`/finances/bonos/calculos/?${query}`);
        if (!res.ok) throw new Error('Error al obtener asignaciones');
        return res.json();
    },

    /**
     * Obtiene info del bono activo del usuario
     * GET /api/v1/finances/bonos/calculos/?page=1&page_size=1
     */
    async getInfoBonoActual() {
        const res = await apiFetch('/finances/bonos/calculos/?page=1&page_size=1');
        if (!res.ok) throw new Error('Error al obtener info de bono');
        const data = await res.json();
        return data.items?.[0] || null;
    },

    /**
     * Obtiene metas vinculadas al bono del usuario
     * (Por ahora mock - requiere endpoint en bonus_service)
     */
    async getMetasVinculadas() {
        // TODO: Implementar cuando exista endpoint en bonus_service
        return [
            { titulo: "Disponibilidad de Servidores", meta: "99.9%", actual: "99.5%", icono: "🖥️" },
            { titulo: "Certificación Cloud", meta: "1", actual: "1", icono: "📜" },
            { titulo: "Feedback de Equipo", meta: "4.5/5", actual: "4.2/5", icono: "🤝" }
        ];
    },

    /**
     * Obtiene historial de pagos del usuario
     * GET /api/v1/finances/bonos/calculos/?page=1&page_size=10
     */
    async getHistorialPagos() {
        const res = await apiFetch('/finances/bonos/calculos/?page=1&page_size=10');
        if (!res.ok) throw new Error('Error al obtener historial');
        const data = await res.json();
        return data.items || [];
    },

    /**
     * Obtiene lista de programas de bono (Admin)
     * GET /api/v1/finances/bonos/programas/
     */
    async getProgramas() {
        const res = await apiFetch('/finances/bonos/programas/');
        if (!res.ok) throw new Error('Error al obtener programas');
        return res.json();
    },

    /**
     * Crea un nuevo programa de bono
     * POST /api/v1/finances/bonos/programas/
     */
    async crearPrograma(data) {
        const res = await apiFetch('/finances/bonos/programas/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error al crear programa');
        return res.json();
    },

    /**
     * Asigna empleado a programa de bono
     * POST /api/v1/finances/bonos/empleados/
     */
    async asignarEmpleado(data) {
        const res = await apiFetch('/finances/bonos/empleados/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error al asignar empleado');
        return res.json();
    },

    /**
     * Registra un pago de bono
     * POST /api/v1/finances/bonos/pagos/
     */
    async registrarPago(data) {
        const res = await apiFetch('/finances/bonos/pagos/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error al registrar pago');
        return res.json();
    }
};

export default BonosService;