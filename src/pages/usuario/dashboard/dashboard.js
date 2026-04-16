/**
 * SERVICIO DE DATOS (Backend Interface)
 */
const UsuarioDashboardService = {
    async getDatosPersonales() {
        // En el futuro: const res = await fetch('/api/perfil'); return res.json();
        return {
            nombre: "Sarah Jenkins",
            promedio: 4.92,
            pendientes: 2,
            vencimiento: "20 de Octubre",
            bono: "$2,450.00"
        };
    },

    async getMisEvaluaciones() {
        return [
            { id: 101, titulo: "Desempeño Trimestral Q3", fecha: "15 Sep, 2023", resultado: 4.8, estado: "Completado", clase: "badge bg-success-subtle text-success" },
            { id: 102, titulo: "Habilidades Técnicas", fecha: "02 Ago, 2023", resultado: 5.0, estado: "Completado", clase: "badge bg-success-subtle text-success" },
            { id: 103, titulo: "Cultura Organizacional", fecha: "10 Jul, 2023", resultado: 4.5, estado: "Completado", clase: "badge bg-success-subtle text-success" }
        ];
    },

    async getMisTareas() {
        return [
            { id: 1, tarea: "Autoevaluación Anual", prioridad: "Alta", fecha: "Hoy", color: "bg-danger" },
            { id: 2, tarea: "Feedback de Pares", prioridad: "Media", fecha: "Mañana", color: "bg-primary" },
            { id: 3, tarea: "Revisión de Objetivos Q4", prioridad: "Baja", fecha: "Próxima semana", color: "bg-info" }
        ];
    }
};

/**
 * CONTROLADOR DE LA VISTA
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Llamada paralela al Backend
        const [perfil, evaluaciones, tareas] = await Promise.all([
            UsuarioDashboardService.getDatosPersonales(),
            UsuarioDashboardService.getMisEvaluaciones(),
            UsuarioDashboardService.getMisTareas()
        ]);

        // Inyectar datos en Tarjetas
        document.getElementById('nombre-usuario').textContent = perfil.nombre;
        document.getElementById('mi-promedio').textContent = perfil.promedio.toFixed(2);
        document.getElementById('mis-pendientes').textContent = perfil.pendientes;
        document.getElementById('fecha-vencimiento').textContent = perfil.vencimiento;
        document.getElementById('mi-bono').textContent = perfil.bono;

        // Renderizar componentes
        renderTabla(evaluaciones);
        renderTareas(tareas);

    } catch (error) {
        console.error("Error al cargar datos del backend:", error);
    }
});

function renderTabla(datos) {
    const tbody = document.getElementById('tabla-mis-evaluaciones');
    tbody.innerHTML = datos.map(ev => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">${ev.titulo}</td>
            <td>${ev.fecha}</td>
            <td class="fw-bold">${ev.resultado.toFixed(1)}</td>
            <td><span class="${ev.clase} rounded-pill px-3 py-1 fw-bold" style="font-size:0.7rem">${ev.estado}</span></td>
        </tr>
    `).join('');
}

function renderTareas(tareas) {
    const lista = document.getElementById('lista-tareas-usuario');
    lista.innerHTML = tareas.map(t => `
        <li class="list-group-item d-flex justify-content-between align-items-start border-0 px-0 py-3 border-bottom">
            <div class="ms-2 me-auto">
                <div class="fw-bold small text-dark-blue">${t.tarea}</div>
                <span class="text-muted" style="font-size: 0.7rem;">Prioridad: ${t.prioridad}</span>
            </div>
            <span class="badge ${t.color} rounded-pill small">${t.fecha}</span>
        </li>
    `).join('');
}