// Simulación de "Servicio de Datos" (Lo que haría el Backend)
const DashboardService = {
    async getResumen() {
        // En el futuro: return fetch('api/resumen').then(r => r.json());
        return { usuarios: 150, evaluaciones: 45, pendientes: 12, bonos: 8 };
    },
    async getActividad() {
        return [
            // Cambiamos los emojis por clases de Bootstrap Icons
            { id: 1, text: 'Nueva evaluación completada', time: 'Hace 5 min', icon: 'bi-check-circle-fill', color: 'text-success' },
            { id: 2, text: 'Nuevo usuario registrado', time: 'Hace 1 hora', icon: 'bi-person-fill', color: 'text-primary' },
            { id: 3, text: 'Bono aprobado', time: 'Hace 3 horas', icon: 'bi-gift-fill', color: 'text-warning' }
        ];
    },
    async getTareas() {
        return [
            { id: 10, title: 'Revisión de evaluaciones', date: 'Hoy', badge: 'bg-primary' },
            { id: 11, title: 'Aprobación de bonos', date: 'Mañana', badge: 'bg-warning text-dark' },
            { id: 12, title: 'Generar reporte mensual', date: 'Próxima semana', badge: 'bg-info text-white' }
        ];
    }
};

// Lógica de Renderizado (Pintar en pantalla)
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
    container.innerHTML = items.map(item => `
        <li class="list-group-item d-flex justify-content-between align-items-center border-0 px-0">
            <div><i class="bi ${item.icon} ${item.color} me-2 fs-5"></i> ${item.text}</div>
            <small class="text-muted">${item.time}</small>
        </li>
    `).join('');
}

function renderTareas(items) {
    const container = document.getElementById('lista-tareas');
    container.innerHTML = items.map(item => `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-secondary">${item.title}</span>
            <span class="badge ${item.badge} p-2">${item.date}</span>
        </div>
    `).join('');
}