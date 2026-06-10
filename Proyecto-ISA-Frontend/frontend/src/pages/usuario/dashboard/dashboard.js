const UsuarioDashboardService = {
    async getMiPerfil() {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        return {
            nombre: userData.nombre_completo || userData.nombre || 'Usuario',
            promedio: 0,
            pendientes: 0,
            vencimiento: '--',
            bono: 'N/A'
        };
    },

    async getMisEvaluaciones() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            return data.results || data;
        } catch {
            return [];
        }
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [perfil, evaluaciones] = await Promise.all([
            UsuarioDashboardService.getMiPerfil(),
            UsuarioDashboardService.getMisEvaluaciones()
        ]);

        const pendientes = evaluaciones.filter(
            e => !['APPROVED', 'CLOSED'].includes(e.estado)
        ).length;

        const completadas = evaluaciones.filter(
            e => ['APPROVED', 'CLOSED'].includes(e.estado)
        );

        const promedio = completadas.length > 0
            ? completadas.reduce((sum, e) => sum + (Number(e.calificacion_global) || 0), 0) / completadas.length
            : 0;

        perfil.pendientes = pendientes;
        perfil.promedio = promedio;

        document.getElementById('nombre-usuario').textContent = perfil.nombre;
        document.getElementById('mi-promedio').textContent = Number(perfil.promedio).toFixed(2);
        document.getElementById('mis-pendientes').textContent = perfil.pendientes;
        document.getElementById('fecha-vencimiento').textContent = perfil.vencimiento;
        document.getElementById('mi-bono').textContent = perfil.bono;

        const mensaje = document.getElementById('mensaje-desempeno');
        if (completadas.length === 0) {
            mensaje.textContent = 'Sin evaluaciones registradas aún';
            mensaje.className = 'text-muted small mb-0';
        } else {
            mensaje.textContent = ' ¡Excelente desempeño!';
            mensaje.className = 'text-success small mb-0';
        }

        renderTabla(evaluaciones);

    } catch (error) {
        console.error("Error al cargar datos del backend:", error);
    }
});

function estadoBadge(estado) {
    const map = {
        'DRAFT': 'badge bg-secondary',
        'SUBMITTED': 'badge bg-info text-dark',
        'PENDING_APPROVAL': 'badge bg-warning text-dark',
        'APPROVED': 'badge bg-success',
        'CLOSED': 'badge bg-dark',
        'REJECTED': 'badge bg-danger'
    };
    return map[estado] || 'badge bg-light text-dark';
}

function renderTabla(datos) {
    const tbody = document.getElementById('tabla-mis-evaluaciones');
    if (!datos || datos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted small py-3">Sin evaluaciones registradas</td></tr>`;
        return;
    }
    tbody.innerHTML = datos.map(ev => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">${ev.periodo_nombre || 'Evaluación'}</td>
            <td>${ev.fecha_creacion ? new Date(ev.fecha_creacion).toLocaleDateString('es-MX') : '--'}</td>
            <td class="fw-bold">${ev.calificacion_global ? Number(ev.calificacion_global).toFixed(1) : '--'}</td>
            <td><span class="${estadoBadge(ev.estado)} rounded-pill px-3 py-1 fw-bold" style="font-size:0.7rem">${ev.estado}</span></td>
        </tr>
    `).join('');
}
