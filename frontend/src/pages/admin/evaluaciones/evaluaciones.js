let grillaSupervision = null;
let todasLasEvaluaciones = [];

const EvalService = {
    async list() {
        const res = await apiFetch('/evaluations/');
        if (!res.ok) return [];
        const data = await res.json();
        return Array.isArray(data) ? data : (data.results || []);
    },

    async getEvaluacion(id) {
        const res = await apiFetch(`/evaluations/${id}/`);
        if (!res.ok) return null;
        return await res.json();
    },

    async crear(data) {
        const res = await apiFetch('/evaluations/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(Object.values(err).flat().join(', ') || 'Error al crear');
        }
        return await res.json();
    },

    async actualizar(id, data) {
        const res = await apiFetch(`/evaluations/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error al actualizar');
        return await res.json();
    },

    async submit(id) {
        const res = await apiFetch(`/evaluations/${id}/submit/`, {
            method: 'POST'
        });
        if (!res.ok) throw new Error('Error al enviar');
        return await res.json();
    },

    async delete(id) {
        const res = await apiFetch(`/evaluations/${id}/`, {
            method: 'DELETE'
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || 'Error al eliminar');
        }
        return true;
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    await cargarEvaluaciones();

    document.getElementById('btn-draft').addEventListener('click', guardarBorrador);
    document.getElementById('btn-publish').addEventListener('click', publicarEvaluacion);
});

async function cargarEvaluaciones() {
    try {
        const evaluaciones = await EvalService.list();
        renderTabla(evaluaciones);
        renderStats(evaluaciones);
    } catch (error) {
        console.error('Error cargando evaluaciones:', error);
    }
}

function renderTabla(evaluaciones) {
    const container = document.getElementById('criteria-container');
    if (!evaluaciones || evaluaciones.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                <p>No hay evaluaciones registradas</p>
                <p class="small">Usa el formulario de la izquierda para crear una nueva evaluación</p>
            </div>`;
        document.getElementById('items-count').textContent = '0 EVALUACIONES';
        return;
    }

    document.getElementById('items-count').textContent = `${evaluaciones.length} EVALUACIONES`;

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover align-middle small">
                <thead class="table-light text-muted text-uppercase">
                    <tr>
                        <th>Evaluado</th>
                        <th>Evaluador</th>
                        <th>Período</th>
                        <th>Estado</th>
                        <th>Calificación</th>
                        <th>Fecha</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    ${evaluaciones.map(ev => `
                        <tr class="align-middle">
                            <td class="fw-bold text-dark-blue">${ev.evaluado_nombre || '—'}</td>
                            <td>${ev.evaluador_nombre || '—'}</td>
                            <td>${ev.periodo_nombre || '—'}</td>
                            <td><span class="badge ${estadoClase(ev.estado)} rounded-pill px-2 py-1">${ev.estado}</span></td>
                            <td class="fw-bold">${ev.calificacion_global ? Number(ev.calificacion_global).toFixed(1) : '—'}</td>
                            <td class="text-muted">${ev.fecha_creacion ? new Date(ev.fecha_creacion).toLocaleDateString('es-MX') : '—'}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="verEvaluacion('${ev.id}')" title="Ver">
                                    <i class="bi bi-eye"></i>
                                </button>
                                ${ev.estado === 'DRAFT' ? `
                                <button class="btn btn-sm btn-outline-danger ms-1" onclick="eliminarEvaluacion('${ev.id}')" title="Eliminar borrador">
                                    <i class="bi bi-trash"></i>
                                </button>` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>`;
}

function renderStats(evaluaciones) {
    const total = evaluaciones.length;
    const completados = evaluaciones.filter(e => ['APPROVED', 'CLOSED'].includes(e.estado)).length;
    const pendientes = evaluaciones.filter(e => ['SUBMITTED', 'PENDING_APPROVAL'].includes(e.estado)).length;
    const borradores = evaluaciones.filter(e => e.estado === 'DRAFT').length;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-completados').textContent = completados;
    document.getElementById('stat-pendientes').textContent = pendientes;
    document.getElementById('stat-borrador').textContent = borradores;
}

function estadoClase(estado) {
    const map = {
        'DRAFT': 'bg-secondary',
        'SUBMITTED': 'bg-info text-dark',
        'PENDING_APPROVAL': 'bg-warning text-dark',
        'APPROVED': 'bg-success',
        'CLOSED': 'bg-dark',
        'REJECTED': 'bg-danger'
    };
    return map[estado] || 'bg-light text-dark';
}

async function guardarBorrador() {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    const evaluadoId = userData.user_id;
    if (!evaluadoId) {
        alert('Debes iniciar sesión para crear una evaluación');
        return;
    }

    try {
        const data = await EvalService.crear({
            evaluado: evaluadoId,
            evaluador: evaluadoId,
            periodo: 1
        });
        alert('Borrador guardado correctamente');
        await cargarEvaluaciones();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function publicarEvaluacion() {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    const evaluadoId = userData.user_id;
    if (!evaluadoId) {
        alert('Debes iniciar sesión');
        return;
    }

    try {
        const data = await EvalService.crear({
            evaluado: evaluadoId,
            evaluador: evaluadoId,
            periodo: 1
        });

        await EvalService.submit(data.id);
        alert('Evaluación creada y enviada correctamente');
        await cargarEvaluaciones();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function verEvaluacion(id) {
    try {
        const ev = await EvalService.getEvaluacion(id);
        if (ev) {
            alert(`Evaluación de ${ev.evaluado_nombre}\nEstado: ${ev.estado}\nPeríodo: ${ev.periodo_nombre}\nCalificación: ${ev.calificacion_global || '—'}`);
        }
    } catch (error) {
        alert('Error al cargar evaluación');
    }
}

async function abrirSupervision() {
    const modal = new bootstrap.Modal(document.getElementById('modalSupervision'));
    modal.show();

    try {
        todasLasEvaluaciones = await EvalService.list();
        const activos = document.getElementById('total-activos-supervision');
        activos.textContent = `${todasLasEvaluaciones.length} Evaluaciones`;

        if (!grillaSupervision) {
            grillaSupervision = new GrillaSupervisor('grilla-supervision-container', {
                data: todasLasEvaluaciones
            });
        } else {
            grillaSupervision.updateData(todasLasEvaluaciones);
        }

        const completados = evaluaciones.filter(e => ['APPROVED', 'CLOSED'].includes(e.estado)).length;
        const pendientes = evaluaciones.filter(e => ['SUBMITTED', 'PENDING_APPROVAL'].includes(e.estado)).length;
        const borradores = evaluaciones.filter(e => e.estado === 'DRAFT').length;

        document.getElementById('stat-total').textContent = evaluaciones.length;
        document.getElementById('stat-completados').textContent = completados;
        document.getElementById('stat-pendientes').textContent = pendientes;
        document.getElementById('stat-borrador').textContent = borradores;
    } catch (error) {
        console.error('Error cargando supervisión:', error);
    }
}

async function eliminarEvaluacion(id) {
    if (!confirm('¿Eliminar esta evaluación en borrador? Esta acción no se puede deshacer.')) return;

    try {
        await EvalService.delete(id);
        await cargarEvaluaciones();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function filtrarUsuarios() {
    const texto = document.getElementById('buscar-usuario').value.toLowerCase().trim();
    const estado = document.getElementById('filtro-estado').value;

    let filtradas = todasLasEvaluaciones;

    if (texto) {
        filtradas = filtradas.filter(ev =>
            (ev.evaluado_nombre || '').toLowerCase().includes(texto) ||
            (ev.evaluador_nombre || '').toLowerCase().includes(texto)
        );
    }

    if (estado) {
        filtradas = filtradas.filter(ev => ev.estado === estado);
    }

    if (grillaSupervision) {
        grillaSupervision.updateData(filtradas);
    }

    document.getElementById('stat-total').textContent = filtradas.length;
}
