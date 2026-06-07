let todasLasSolicitudes = [];
let todoElHistorial = [];

const SolicitudesService = {
    async getPendientes() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            const evals = Array.isArray(data) ? data : (data.results || []);
            return evals.filter(e => e.estado === 'SUBMITTED' || e.estado === 'PENDING_APPROVAL').map(e => {
                const nivelAprobacion = e.estado === 'SUBMITTED' ? 'Nivel 1 (Evaluador)' : 'Nivel 2 (Manager)';
                const estadoLabel = e.estado === 'SUBMITTED' ? 'Por aprobar (N1)' : 'Por aprobar (N2)';
                return {
                    id: e.id,
                    tipo: 'EVALUACIÓN',
                    titulo: `Evaluación de ${e.evaluado_nombre || 'colaborador'}`,
                    solicitante: e.evaluado_nombre || e.evaluado || '—',
                    puesto: e.evaluado_puesto || '—',
                    fecha: e.fecha_actualizacion || e.fecha_creacion || '',
                    resumen: e.comentarios_evaluador || 'Sin comentarios',
                    nivelAprobacion: nivelAprobacion,
                    estadoLabel: estadoLabel,
                    monto: 'N/A',
                    icono: 'bi-ui-checks',
                    colorIcono: 'text-primary',
                    bgIcono: 'bg-light-blue',
                    badgeColor: e.estado === 'SUBMITTED' ? 'bg-warning-subtle text-warning' : 'bg-info-subtle text-info',
                    estado: e.estado
                };
            });
        } catch {
            return [];
        }
    },
    async getHistorial() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            const evals = Array.isArray(data) ? data : (data.results || []);
            return evals.filter(e => e.estado === 'APPROVED' || e.estado === 'CLOSED' || e.estado === 'REJECTED').map(e => ({
                entidad: `Evaluación de ${e.evaluado_nombre || 'colaborador'}`,
                tipo: 'EVALUACIÓN',
                accion: e.estado === 'REJECTED' ? 'Rechazo' : 'Aprobación',
                fecha: e.fecha_actualizacion || e.fecha_creacion || '',
                resultado: e.estado === 'APPROVED' ? 'APROBADO' : (e.estado === 'CLOSED' ? 'CERRADO' : (e.estado === 'REJECTED' ? 'RECHAZADO' : e.estado)),
                statusClass: e.estado === 'REJECTED' ? 'pill-denied' : 'pill-approved',
                aprobador: e.historial && e.historial.length > 0 ? (e.historial[e.historial.length - 1].usuario_nombre || '—') : '—'
            }));
        } catch {
            return [];
        }
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    todasLasSolicitudes = await SolicitudesService.getPendientes();
    todoElHistorial = await SolicitudesService.getHistorial();
    filtrarSolicitudes('TODAS');
});

function filtrarSolicitudes(categoria, event) {
    if (event) event.preventDefault();

    document.querySelectorAll('.filter-link').forEach(link => link.classList.remove('active'));

    if (event) {
        event.target.classList.add('active');
    } else {
        document.getElementById('filter-all').classList.add('active');
    }

    const solicitudesFiltradas = categoria === 'TODAS'
        ? todasLasSolicitudes
        : todasLasSolicitudes.filter(s => s.tipo === categoria);

    renderizarLista(solicitudesFiltradas);

    const historialFiltrado = categoria === 'TODAS'
        ? todoElHistorial
        : todoElHistorial.filter(h => h.tipo === categoria);

    renderizarHistorial(historialFiltrado);

    if (solicitudesFiltradas.length > 0) {
        verDetalle(solicitudesFiltradas[0].id);
    } else {
        document.getElementById('detalle-revision').innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-inbox text-muted fs-1"></i>
                <p class="text-muted mt-2">No hay solicitudes pendientes en esta categoría.</p>
            </div>`;
    }
}

function renderizarLista(items) {
    const contenedor = document.getElementById('lista-solicitudes');
    contenedor.innerHTML = items.map(item => `
        <div class="card border-0 shadow-sm mb-3 p-4 card-solicitud" onclick="verDetalle('${item.id}')">
            <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center flex-grow-1">
                    <div class="icon-box me-4 ${item.bgIcono} ${item.colorIcono}">
                        <i class="bi ${item.icono}"></i>
                    </div>
                    <div>
                        <h6 class="fw-bold mb-1 text-dark-blue fs-5">${item.titulo}</h6>
                        <small class="text-muted"><i class="bi bi-person-fill me-1"></i> Solicitado por: <strong class="text-dark">${item.solicitante}</strong></small>
                        <br><small class="text-muted"><i class="bi bi-layers me-1"></i> ${item.nivelAprobacion}</small>
                    </div>
                </div>
                <div class="d-flex flex-column align-items-end gap-2">
                    <span class="badge ${item.badgeColor} border-0 px-2 py-1 text-uppercase" style="font-size: 0.65rem; letter-spacing: 0.5px;">${item.estadoLabel || item.estado || item.tipo}</span>
                    <small class="text-muted"><i class="bi bi-calendar3 me-1"></i> ${item.fecha ? new Date(item.fecha).toLocaleDateString() : ''}</small>
                </div>
            </div>
        </div>
    `).join('');
}

let solicitudIdActual = null;

function verDetalle(id) {
    solicitudIdActual = id;
    const item = todasLasSolicitudes.find(s => s.id === id);
    if (!item) return;

    const nivelBadge = item.estado === 'SUBMITTED'
        ? '<span class="badge bg-warning-subtle text-warning px-2 py-1">Nivel 1: Evaluador</span>'
        : '<span class="badge bg-info-subtle text-info px-2 py-1">Nivel 2: Manager del Evaluador</span>';

    const detalle = document.getElementById('detalle-revision');
    detalle.innerHTML = `
        <div class="card border-0 mb-3 bg-transparent">
            <div class="d-flex align-items-center gap-3">
                <div class="rounded-circle d-flex justify-content-center align-items-center" style="width: 45px; height: 45px; background-color: #2c3e50; color: white;">
                    <i class="bi bi-person-fill fs-4"></i>
                </div>
                <div>
                    <h6 class="fw-bold mb-0 text-dark-blue">${item.solicitante}</h6>
                    <small class="text-muted" style="font-size: 0.7rem; letter-spacing: 0.5px;">${item.puesto}</small>
                </div>
            </div>
        </div>

        <div class="card border-0 mb-3 p-3 shadow-sm bg-white" style="border-radius: 10px;">
            <label class="small text-muted text-uppercase mb-1" style="font-size: 0.65rem; letter-spacing: 0.5px;">Tipo de Solicitud</label>
            <p class="fw-bold text-dark-blue mb-0 fs-6">${item.titulo}</p>
        </div>

        <div class="d-flex gap-2 mb-3">
            ${nivelBadge}
            <span class="badge bg-light text-dark px-2 py-1">${item.estado}</span>
        </div>

        <div class="card border-0 mb-3 p-3 shadow-sm bg-white" style="border-radius: 10px;">
            <label class="small text-muted text-uppercase mb-1" style="font-size: 0.65rem; letter-spacing: 0.5px;">Nivel de Aprobación</label>
            <p class="fw-bold mb-0">${item.nivelAprobacion}</p>
        </div>

        <div class="card border-0 mb-3 p-3 shadow-sm bg-white" style="border-radius: 10px;">
            <label class="small text-muted text-uppercase mb-1" style="font-size: 0.65rem; letter-spacing: 0.5px;">Resumen</label>
            <p class="small text-muted mb-0 lh-sm">${item.resumen}</p>
        </div>
    `;
}

function renderizarHistorial(items) {
    const contenedor = document.getElementById('lista-historial');

    if (items.length === 0) {
        contenedor.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4 text-muted">
                    No hay registros históricos para esta categoría.
                </td>
            </tr>`;
        return;
    }

    contenedor.innerHTML = items.map(item => `
        <tr style="border-bottom: 1px solid #eef4ff;">
            <td class="py-3 px-4 fw-bold text-dark-blue">${item.entidad}</td>
            <td class="py-3 text-secondary">${item.accion}</td>
            <td class="py-3 text-secondary">${item.fecha ? new Date(item.fecha).toLocaleDateString() : ''}</td>
            <td class="py-3">
                <span class="badge ${item.statusClass} px-3 py-2 text-uppercase" style="font-size: 0.65rem; letter-spacing: 0.5px;">${item.resultado}</span>
            </td>
            <td class="py-3 px-4 fw-bold text-dark-blue">${item.aprobador}</td>
        </tr>
    `).join('');
}

async function procesarAccion(esAprobado) {
    if (!solicitudIdActual) {
        alert('Por favor, selecciona una solicitud primero.');
        return;
    }

    const accion = esAprobado ? "APROBAR" : "RECHAZAR";
    const confirmacion = confirm(`¿Estás seguro de que deseas ${accion} esta evaluación?`);

    if (!confirmacion) return;

    const btnId = esAprobado ? 'btn-confirmar' : 'btn-rechazar';
    const btnOriginalText = document.getElementById(btnId).innerText;
    document.getElementById(btnId).innerText = "Procesando...";
    document.getElementById(btnId).disabled = true;

    try {
        const endpoint = esAprobado ? 'approve' : 'reject';
        const res = await apiFetch(`/evaluations/${solicitudIdActual}/${endpoint}/`, {
            method: 'POST',
            body: JSON.stringify({ comentario: esAprobado ? 'Aprobado' : 'Rechazado' })
        });

        if (res.ok) {
            alert(`Solicitud ${esAprobado ? 'APROBADA' : 'RECHAZADA'} con éxito.`);
            todasLasSolicitudes = await SolicitudesService.getPendientes();
            todoElHistorial = await SolicitudesService.getHistorial();
            filtrarSolicitudes('TODAS');
        } else {
            const err = await res.json().catch(() => ({}));
            alert(`Error: ${err.detail || 'No se pudo procesar la solicitud'}`);
        }
    } catch (err) {
        alert('Error de conexión al procesar la solicitud');
    } finally {
        document.getElementById(btnId).innerText = btnOriginalText;
        document.getElementById(btnId).disabled = false;
    }
}

document.getElementById('btn-confirmar').addEventListener('click', () => procesarAccion(true));
document.getElementById('btn-rechazar').addEventListener('click', () => procesarAccion(false));
