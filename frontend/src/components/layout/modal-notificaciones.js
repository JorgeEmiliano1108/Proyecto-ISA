const NotificacionesService = {
    getAll() {
        const data = localStorage.getItem('isa_notificaciones');
        return data ? JSON.parse(data) : [];
    },

    save(notificaciones) {
        localStorage.setItem('isa_notificaciones', JSON.stringify(notificaciones));
    },

    create(notificacion) {
        const notificaciones = this.getAll();
        notificacion.id = Date.now();
        notificacion.fecha = new Date().toISOString().split('T')[0];
        notificaciones.unshift(notificacion);
        this.save(notificaciones);
    },

    marcarLeido(id) {
        const notificaciones = this.getAll();
        const idx = notificaciones.findIndex(n => n.id === id);
        if (idx !== -1) {
            notificaciones[idx].leido = true;
            this.save(notificaciones);
        }
    },

    getNoLeidas() {
        return this.getAll().filter(n => !n.leido);
    },

    delete(id) {
        const notificaciones = this.getAll().filter(n => n.id !== id);
        this.save(notificaciones);
    }
};

function renderNotificacionesDropdown(userRol) {
    const notificaciones = NotificacionesService.getAll();
    const noLeidas = notificaciones.filter(n => !n.leido);
    const badgeCount = noLeidas.length;

    return `
        <div class="dropdown" id="dropdown-notificaciones">
            <div class="position-relative hover-icon" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false" style="cursor: pointer;" onclick="marcarTodasLeidas()">
                <i class="bi bi-bell fs-5 text-dark"></i>
                ${badgeCount > 0 ? `<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem; padding: 0.3em 0.5em;">${badgeCount}</span>` : ''}
            </div>
            <div class="dropdown-menu dropdown-menu-end shadow border-0 mt-3" style="width: 350px; max-height: 400px; overflow-y: auto; border-radius: 10px;">
                <div class="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
                    <h6 class="mb-0 fw-bold">Notificaciones</h6>
                    ${badgeCount > 0 ? `<span class="badge bg-primary-subtle text-primary">${badgeCount} nuevas</span>` : ''}
                </div>
                ${notificaciones.length === 0 ? `
                    <div class="text-center py-4 text-muted">
                        <i class="bi bi-bell-slash fs-1"></i>
                        <p class="mb-0 mt-2 small">Sin notificaciones</p>
                    </div>
                ` : notificaciones.slice(0, 10).map(n => `
                    <div class="dropdown-item border-bottom ${n.leido ? 'bg-light-subtle' : 'bg-primary-subtle'}" onclick="verDetalleNotificacion(${n.id})" style="cursor: pointer; white-space: normal;">
                        <div class="d-flex gap-2">
                            <div class="mt-1">
                                <i class="bi ${n.tipo === 'tarea' ? 'bi-exclamation-circle text-warning' : 'bi-megaphone text-info'}"></i>
                            </div>
                            <div class="flex-grow-1">
                                <div class="fw-bold small">${n.titulo}</div>
                                <div class="text-muted small text-truncate">${n.mensaje}</div>
                                <div class="text-muted" style="font-size: 0.7rem;">${n.fechaLimite ? 'Límite: ' + n.fechaLimite : n.fecha}</div>
                            </div>
                            ${n.leido ? '' : '<div class="badge bg-primary">Nuevo</div>'}
                        </div>
                    </div>
                `).join('')}
                <div class="px-3 py-2 text-center">
                    <button class="btn btn-sm btn-outline-secondary w-100" onclick="event.stopPropagation(); verTodasNotificaciones()">Ver todas las notificaciones</button>
                </div>
            </div>
        </div>
    `;
}

function renderBotonAdminNotificaciones() {
    return `
        <button class="dropdown-item py-2" onclick="event.stopPropagation(); abrirModalCrearNotificacion()">
            <i class="bi bi-send me-2 text-muted"></i> Enviar Notificación
        </button>
    `;
}

function marcarTodasLeidas() {
    const notificaciones = NotificacionesService.getAll();
    let cambios = false;
    notificaciones.forEach(n => {
        if (!n.leido) {
            n.leido = true;
            cambios = true;
        }
    });
    if (cambios) {
        NotificacionesService.save(notificaciones);
    }
}

function verDetalleNotificacion(id) {
    const notificaciones = NotificacionesService.getAll();
    const n = notificaciones.find(x => x.id === id);
    if (n) {
        NotificacionesService.marcarLeido(id);
        const modalEl = document.getElementById('modalDetalleNotificacion') || crearModalDetalleNotificacion();
        const modal = new bootstrap.Modal(modalEl);
        modalEl.querySelector('#detalle-notificacion-titulo').textContent = n.titulo;
        modalEl.querySelector('#detalle-notificacion-mensaje').textContent = n.mensaje;
        modalEl.querySelector('#detalle-notificacion-tipo').textContent = n.tipo === 'tarea' ? 'Tarea' : 'Comunicado';
        modalEl.querySelector('#detalle-notificacion-fecha').textContent = n.fechaLimite ? 'Fecha límite: ' + n.fechaLimite : 'Fecha: ' + n.fecha;
        modal.show();
    }
}

function verTodasNotificaciones() {
    const dropdown = document.getElementById('dropdown-notificaciones');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
    window.location.href = '../notificaciones/notificaciones.html';
}

function abrirModalCrearNotificacion() {
    const modal = new bootstrap.Modal(document.getElementById('modalCrearNotificacion'));
    modal.show();
}

function crearNotificacion() {
    const titulo = document.getElementById('notif-titulo').value;
    const mensaje = document.getElementById('notif-mensaje').value;
    const tipo = document.getElementById('notif-tipo').value;
    const fechaLimite = document.getElementById('notif-fecha').value;
    const para = document.getElementById('notif-para').value;

    if (!titulo || !mensaje) {
        alert('Completa título y mensaje');
        return;
    }

    NotificacionesService.create({
        titulo,
        mensaje,
        tipo,
        fechaLimite: fechaLimite || null,
        para,
        leido: false
    });

    bootstrap.Modal.getInstance(document.getElementById('modalCrearNotificacion')).hide();
    document.getElementById('form-crear-notificacion').reset();
    alert('Notificación enviada');
}

function crearModalDetalleNotificacion() {
    const div = document.createElement('div');
    div.id = 'modalDetalleNotificacion';
    div.className = 'modal fade';
    div.tabIndex = -1;
    div.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold" id="detalle-notificacion-titulo"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <span class="badge bg-secondary mb-2" id="detalle-notificacion-tipo"></span>
                    <p class="mt-2" id="detalle-notificacion-mensaje"></p>
                    <p class="text-muted small mt-3" id="detalle-notificacion-fecha"></p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(div);
    return div;
}

function crearModalCrearNotificacion() {
    if (document.getElementById('modalCrearNotificacion')) return;
    
    const div = document.createElement('div');
    div.id = 'modalCrearNotificacion';
    div.className = 'modal fade';
    div.tabIndex = -1;
    div.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold">📢 Enviar Notificación</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="form-crear-notificacion">
                        <div class="mb-3">
                            <label class="form-label">Tipo</label>
                            <select class="form-select" id="notif-tipo">
                                <option value="comunicado">Comunicado</option>
                                <option value="tarea">Tarea</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Título</label>
                            <input type="text" class="form-control" id="notif-titulo" required placeholder="Título de la notificación">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Mensaje</label>
                            <textarea class="form-control" id="notif-mensaje" rows="3" required placeholder="Escribe el mensaje..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Fecha límite (opcional)</label>
                            <input type="date" class="form-control" id="notif-fecha">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Para</label>
                            <select class="form-select" id="notif-para">
                                <option value="todos">Todos los usuarios</option>
                                <option value="usuario">Un usuario específico</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="crearNotificacion()">Enviar</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(div);
    return div;
}