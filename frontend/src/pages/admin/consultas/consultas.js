document.addEventListener("DOMContentLoaded", async () => {
    crearModalResponder();
    await renderConsultas();
    await renderHistorialNotificaciones();
    actualizarStats();
    window.NotificacionesService = NotificacionesService;
    window.crearNotificacionDesdeAclaraciones = crearNotificacionDesdeAclaraciones;
    window.renderHistorialNotificaciones = renderHistorialNotificaciones;
});

const ConsultasService = {
    async getAll() {
        const res = await apiFetch('/consultas/');
        if (!res.ok) return [];
        const data = await res.json();
        return Array.isArray(data) ? data : (data.results || []);
    },

    async getPendientes() {
        const res = await apiFetch('/consultas/?estado=pendiente');
        if (!res.ok) return [];
        const data = await res.json();
        return Array.isArray(data) ? data : (data.results || []);
    },

    async getRespondidas() {
        const res = await apiFetch('/consultas/?estado=respondido');
        if (!res.ok) return [];
        const data = await res.json();
        return Array.isArray(data) ? data : (data.results || []);
    },

    async responder(id, respuesta) {
        const res = await apiFetch(`/consultas/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify({
                respuesta,
                estado: 'respondido',
                fecha_respuesta: new Date().toISOString()
            })
        });
        return res.ok;
    },

    async eliminar(id) {
        const res = await apiFetch(`/consultas/${id}/`, { method: 'DELETE' });
        return res.ok;
    }
};

async function renderConsultas() {
    await renderPendientes();
    await renderRespondidas();
    actualizarStats();
}

async function renderPendientes() {
    const consultas = await ConsultasService.getPendientes();
    const tbody = document.getElementById('tabla-pendientes');

    if (consultas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4">
                    <div class="empty-state">
                        <i class="bi bi-check-circle"></i>
                        <h5>No hay consultas pendientes</h5>
                        <p class="mb-0">Los usuarios no han enviado consultas aún.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = consultas.map(c => `
        <tr>
            <td class="px-4">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                        ${(c.nombre_usuario || c.usuario_nombre || '?').charAt(0)}
                    </div>
                    <span class="fw-bold">${c.nombre_usuario || c.usuario_nombre || 'Usuario'}</span>
                </div>
            </td>
            <td><span class="text-muted">${c.fecha ? new Date(c.fecha).toLocaleDateString() : '-'}</span></td>
            <td><span class="consulta-texto">${c.pregunta}</span></td>
            <td class="text-end px-4">
                <button class="btn btn-success btn-action me-2" onclick="abrirResponder('${c.id}')" title="Responder">
                    <i class="bi bi-reply"></i>
                </button>
                <button class="btn btn-outline-danger btn-action" onclick="eliminarConsulta('${c.id}')" title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function renderRespondidas() {
    const consultas = await ConsultasService.getRespondidas();
    const tbody = document.getElementById('tabla-respondidas');

    if (consultas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5">
                    <div class="empty-state">
                        <i class="bi bi-chat-square-text"></i>
                        <h5>No hay consultas respondidas</h5>
                        <p class="mb-0">Las consultas respondidas aparecerán aquí.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = consultas.map(c => `
        <tr>
            <td class="px-4">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                        ${(c.nombre_usuario || c.usuario_nombre || '?').charAt(0)}
                    </div>
                    <span class="fw-bold">${c.nombre_usuario || c.usuario_nombre || 'Usuario'}</span>
                </div>
            </td>
            <td><span class="text-muted">${c.fecha ? new Date(c.fecha).toLocaleDateString() : '-'}</span></td>
            <td><span class="consulta-texto">${c.pregunta}</span></td>
            <td><span class="respuesta-texto">${c.respuesta || ''}</span></td>
            <td class="text-end px-4">
                <button class="btn btn-outline-danger btn-action" onclick="eliminarConsulta('${c.id}')" title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function actualizarStats() {
    Promise.all([
        ConsultasService.getPendientes(),
        ConsultasService.getRespondidas(),
        NotificacionesService.getAll()
    ]).then(([pendientes, respondidas, notificaciones]) => {
        document.getElementById('stat-pendientes').textContent = pendientes.length;
        document.getElementById('stat-respondidas').textContent = respondidas.length;
        document.getElementById('stat-total').textContent = pendientes.length + respondidas.length;
        document.getElementById('stat-notificaciones').textContent = notificaciones.length;
        document.getElementById('badge-pendientes').textContent = pendientes.length;
    });
}

let consultaIdActual = null;

async function abrirResponder(id) {
    consultaIdActual = id;
    const consultas = await ConsultasService.getAll();
    const c = consultas.find(x => x.id === id);
    if (c) {
        document.getElementById('respuesta-usuario').textContent = c.nombre_usuario || c.usuario_nombre || 'Usuario';
        document.getElementById('respuesta-fecha').textContent = c.fecha ? new Date(c.fecha).toLocaleDateString() : '-';
        document.getElementById('respuesta-pregunta').textContent = c.pregunta;
        document.getElementById('respuesta-texto').value = '';
        const modal = new bootstrap.Modal(document.getElementById('modalResponder'));
        modal.show();
    }
}

async function enviarRespuesta() {
    const respuesta = document.getElementById('respuesta-texto').value.trim();
    if (!respuesta) {
        alert('Escribe una respuesta');
        return;
    }

    const ok = await ConsultasService.responder(consultaIdActual, respuesta);
    bootstrap.Modal.getInstance(document.getElementById('modalResponder')).hide();
    await renderConsultas();
    actualizarStats();
    if (ok) {
        alert('Respuesta enviada');
    } else {
        alert('Error al enviar respuesta');
    }
}

async function eliminarConsulta(id) {
    if (confirm('¿Eliminar esta consulta?')) {
        const ok = await ConsultasService.eliminar(id);
        await renderConsultas();
        actualizarStats();
    }
}

async function exportarConsultas() {
    const consultas = await ConsultasService.getAll();
    let csv = 'Usuario,Fecha,Consulta,Respuesta,Estado,Fecha Respuesta\n';
    consultas.forEach(c => {
        csv += `"${c.nombre_usuario || ''}","${c.fecha || ''}","${(c.pregunta || '').replace(/"/g, '""')}","${(c.respuesta || '').replace(/"/g, '""')}","${c.estado || ''}","${c.fecha_respuesta || ''}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'consultas_' + new Date().toISOString().split('T')[0] + '.csv';
    a.click();
    URL.revokeObjectURL(url);
}

async function crearNotificacionDesdeAclaraciones() {
    const titulo = document.getElementById('notif-titulo').value;
    const mensaje = document.getElementById('notif-mensaje').value;
    const tipo = document.getElementById('notif-tipo').value;
    const fechaLimite = document.getElementById('notif-fecha').value;

    if (!titulo || !mensaje) {
        alert('Completa título y mensaje');
        return;
    }

    const ok = await NotificacionesService.create({
        titulo,
        mensaje,
        tipo,
        fecha_limite: fechaLimite || null,
        para: 'todos',
        leido: false
    });

    if (!ok) {
        alert('Error al enviar notificación');
        return;
    }

    document.getElementById('notif-titulo').value = '';
    document.getElementById('notif-mensaje').value = '';
    document.getElementById('notif-fecha').value = '';

    await renderHistorialNotificaciones();
    actualizarStats();
    alert('Notificación enviada correctamente');
}

async function renderHistorialNotificaciones() {
    const notificaciones = await NotificacionesService.getAll();
    const contenedor = document.getElementById('lista-historial-notificaciones');

    if (notificaciones.length === 0) {
        contenedor.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-1"></i>
                <p class="mb-0 mt-2">No hay notificaciones enviadas</p>
            </div>
        `;
        return;
    }

    contenedor.innerHTML = notificaciones.map(n => `
        <div class="border-bottom py-3">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <span class="badge ${n.tipo === 'tarea' ? 'bg-warning' : 'bg-info'}">${n.tipo === 'tarea' ? 'Tarea' : 'Comunicado'}</span>
                    <span class="ms-2 fw-bold">${n.titulo}</span>
                </div>
                <span class="text-muted small">${n.fecha_creacion ? new Date(n.fecha_creacion).toLocaleDateString() : ''}</span>
            </div>
            <p class="mb-0 mt-2 small text-muted">${n.mensaje}</p>
            ${n.fecha_limite ? `<p class="mb-0 small text-danger">Límite: ${n.fecha_limite}</p>` : ''}
        </div>
    `).join('');
}

function crearModalResponder() {
    if (document.getElementById('modalResponder')) return;

    const div = document.createElement('div');
    div.id = 'modalResponder';
    div.className = 'modal fade';
    div.tabIndex = -1;
    div.innerHTML = `
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold">Responder Consulta</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="bg-light rounded p-3 mb-3">
                        <div class="d-flex justify-content-between mb-2">
                            <span class="fw-bold" id="respuesta-usuario"></span>
                            <span class="text-muted small" id="respuesta-fecha"></span>
                        </div>
                        <p class="mb-0" id="respuesta-pregunta"></p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Tu respuesta</label>
                        <textarea class="form-control" id="respuesta-texto" rows="4" placeholder="Escribe tu respuesta..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="enviarRespuesta()">Enviar Respuesta</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(div);
}
