const ConsultasService = {
    getAll() {
        const data = localStorage.getItem('isa_consultas');
        return data ? JSON.parse(data) : [];
    },

    save(consultas) {
        localStorage.setItem('isa_consultas', JSON.stringify(consultas));
    },

    create(consulta) {
        const consultas = this.getAll();
        const userData = JSON.parse(localStorage.getItem('userData'));
        consulta.id = Date.now();
        consulta.usuario = userData.nombre;
        consulta.fecha = new Date().toISOString().split('T')[0];
        consulta.estado = 'pendiente';
        consulta.respuesta = null;
        consultas.unshift(consulta);
        this.save(consultas);
    },

    getMisConsultas() {
        const userData = JSON.parse(localStorage.getItem('userData'));
        return this.getAll().filter(c => c.usuario === userData.nombre);
    },

    getPendientes() {
        return this.getAll().filter(c => c.estado === 'pendiente');
    },

    getRespondidas() {
        return this.getAll().filter(c => c.estado === 'respondido');
    },

    responder(id, respuesta) {
        const consultas = this.getAll();
        const idx = consultas.findIndex(c => c.id === id);
        if (idx !== -1) {
            consultas[idx].respuesta = respuesta;
            consultas[idx].estado = 'respondido';
            consultas[idx].fechaRespuesta = new Date().toISOString().split('T')[0];
            this.save(consultas);
        }
    }
};

function abrirModalConsulta() {
    const modal = new bootstrap.Modal(document.getElementById('modalConsulta'));
    modal.show();
}

function renderDropdownAyuda() {
    return `
        <div class="dropdown" id="dropdown-ayuda">
            <div class="hover-icon" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false" style="cursor: pointer;">
                <i class="bi bi-question-circle fs-5 text-dark"></i>
            </div>
            <div class="dropdown-menu dropdown-menu-end shadow border-0 mt-3" style="width: 320px; border-radius: 10px;">
                <div class="px-3 py-2 border-bottom">
                    <h6 class="mb-0 fw-bold">❓ Centro de Ayuda</h6>
                </div>
                <div class="p-3">
                    <p class="small text-muted mb-3">¿Tienes alguna duda? Envía tu consulta y el administrador te responderá.</p>
                    <button class="btn btn-primary w-100" onclick="abrirModalConsulta()">
                        <i class="bi bi-send me-2"></i> Nueva Consulta
                    </button>
                </div>
                <div class="border-top">
                    <button class="dropdown-item py-2" onclick="verMisConsultas()">
                        <i class="bi bi-chat-dots me-2 text-muted"></i> Ver mis consultas
                    </button>
                </div>
            </div>
        </div>
    `;
}

function renderBotonAdminConsultas() {
    const pendientes = ConsultasService.getPendientes().length;
    return `
        <button class="dropdown-item py-2" onclick="window.location.href='../consultas/consultas.html'">
            <i class="bi bi-chat-dots me-2 text-muted"></i> Aclaraciones 
            ${pendientes > 0 ? `<span class="badge bg-danger">${pendientes}</span>` : ''}
        </button>
    `;
}

function verMisConsultas() {
    const modal = new bootstrap.Modal(document.getElementById('modalMisConsultas') || crearModalMisConsultas());
    renderMisConsultasLista();
    modal.show();
}

function renderMisConsultasLista() {
    const consultas = ConsultasService.getMisConsultas();
    const contenedor = document.getElementById('lista-mis-consultas');
    
    if (consultas.length === 0) {
        contenedor.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-chat-square-text fs-1"></i>
                <p class="mt-2">No has enviado consultas</p>
            </div>
        `;
        return;
    }

    contenedor.innerHTML = consultas.map(c => `
        <div class="border-bottom py-3">
            <div class="d-flex justify-content-between align-items-start">
                <div class="fw-bold small">${c.fecha}</div>
                <span class="badge ${c.estado === 'pendiente' ? 'bg-warning' : 'bg-success'}">${c.estado === 'pendiente' ? 'Pendiente' : 'Respondido'}</span>
            </div>
            <p class="mb-1 mt-2">${c.pregunta}</p>
            ${c.respuesta ? `
                <div class="bg-light rounded p-2 mt-2">
                    <div class="small text-muted">Respuesta:</div>
                    <small>${c.respuesta}</small>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function crearModalMisConsultas() {
    const div = document.createElement('div');
    div.id = 'modalMisConsultas';
    div.className = 'modal fade';
    div.tabIndex = -1;
    div.innerHTML = `
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold">💬 Mis Consultas</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="lista-mis-consultas">
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

function crearModalConsulta() {
    if (document.getElementById('modalConsulta')) return;
    
    const div = document.createElement('div');
    div.id = 'modalConsulta';
    div.className = 'modal fade';
    div.tabIndex = -1;
    div.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold">💬 Nueva Consulta</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="form-consulta">
                        <div class="mb-3">
                            <label class="form-label">Tu duda o pregunta</label>
                            <textarea class="form-control" id="consulta-pregunta" rows="4" required placeholder="Describe tu duda o pregunta..."></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="enviarConsulta()">Enviar Consulta</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(div);
    return div;
}

function enviarConsulta() {
    const pregunta = document.getElementById('consulta-pregunta').value;
    if (!pregunta) {
        alert('Escribe tu consulta');
        return;
    }

    ConsultasService.create({ pregunta });
    bootstrap.Modal.getInstance(document.getElementById('modalConsulta')).hide();
    document.getElementById('consulta-pregunta').value = '';
    alert('Consulta enviada. Te responderemos pronto.');
}