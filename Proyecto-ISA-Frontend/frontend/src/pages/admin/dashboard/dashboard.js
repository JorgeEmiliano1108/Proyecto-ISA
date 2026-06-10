const DashboardService = {
    async getResumen() {
        try {
            const [usersRes, evalsRes] = await Promise.all([
                apiFetch('/users/'),
                apiFetch('/evaluations/')
            ]);

            let totalUsuarios = 0;
            if (usersRes.ok) {
                const usersData = await usersRes.json();
                totalUsuarios = Array.isArray(usersData) ? usersData.length : (usersData.count || usersData.results?.length || 0);
            }

            let totalEvals = 0;
            let pendientes = 0;
            if (evalsRes.ok) {
                const evalsData = await evalsRes.json();
                const evals = Array.isArray(evalsData) ? evalsData : (evalsData.results || []);
                totalEvals = evals.length;
                pendientes = evals.filter(e => !['APPROVED', 'CLOSED'].includes(e.estado)).length;
            }

            return { usuarios: totalUsuarios, evaluaciones: totalEvals, pendientes, bonos: '—' };
        } catch {
            return { usuarios: '—', evaluaciones: '—', pendientes: '—', bonos: '—' };
        }
    },

    async getActividad() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            const evals = Array.isArray(data) ? data : (data.results || []);

            return evals.slice(0, 5).map(e => ({
                id: e.id,
                text: `Evaluación ${e.estado} - ${e.evaluado_nombre || e.evaluado}`,
                time: e.fecha_actualizacion || e.fecha_creacion || '',
                icon: e.estado === 'APPROVED' ? 'bi-check-circle-fill' : 'bi-hourglass-split',
                color: e.estado === 'APPROVED' ? 'text-success' : 'text-warning'
            }));
        } catch {
            return [];
        }
    },

    async getTareas() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            const evals = Array.isArray(data) ? data : (data.results || []);

            const pendientes = evals.filter(e => !['APPROVED', 'CLOSED'].includes(e.estado));
            return pendientes.slice(0, 5).map(e => ({
                id: e.id,
                title: `Revisar evaluación de ${e.evaluado_nombre || 'colaborador'}`,
                date: `Pendiente`,
                badge: 'bg-warning text-dark'
            }));
        } catch {
            return [];
        }
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [resumen, actividad, tareas] = await Promise.all([
            DashboardService.getResumen(),
            DashboardService.getActividad(),
            DashboardService.getTareas()
        ]);

        renderStats(resumen);
        renderActividad(actividad);
        renderTareas(tareas);
    } catch (error) {
        console.error("Error cargando datos del dashboard:", error);
    }
});

function renderStats(data) {
    document.getElementById('stat-usuarios').textContent = data.usuarios;
    document.getElementById('stat-evaluaciones').textContent = data.evaluaciones;
    document.getElementById('stat-pendientes').textContent = data.pendientes;
    document.getElementById('stat-bonos').textContent = data.bonos;
}

function renderActividad(items) {
    const container = document.getElementById('lista-actividad');
    if (!items || items.length === 0) {
        container.innerHTML = '<li class="list-group-item border-0 text-muted small">Sin actividad reciente</li>';
        return;
    }
    container.innerHTML = items.map(item => `
        <li class="list-group-item d-flex justify-content-between align-items-center border-0 px-0">
            <div><i class="bi ${item.icon} ${item.color} me-2 fs-5"></i> ${item.text}</div>
            <small class="text-muted">${item.time ? new Date(item.time).toLocaleDateString('es-MX') : '—'}</small>
        </li>
    `).join('');
}

function renderTareas(items) {
    const container = document.getElementById('lista-tareas');
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="text-muted small">Sin tareas pendientes</div>';
        return;
    }
    container.innerHTML = items.map(item => `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-secondary">${item.title}</span>
            <span class="badge ${item.badge} p-2">${item.date}</span>
        </div>
    `).join('');
}
