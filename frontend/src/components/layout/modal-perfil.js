const PerfilService = {
    getPerfil() {
        const data = localStorage.getItem('isa_perfil');
        return data ? JSON.parse(data) : null;
    },

    save(perfil) {
        localStorage.setItem('isa_perfil', JSON.stringify(perfil));
    },

    getDefault() {
        const userData = JSON.parse(localStorage.getItem('userData'));
        return {
            nombre: userData.nombre,
            email: userData.nombre.toLowerCase().replace(' ', '.') + '@isa.com',
            telefono: '',
            departamento: '',
            puesto: '',
            foto: null
        };
    }
};

function abrirModalPerfil() {
    const modalEl = document.getElementById('modalPerfil') || crearModalPerfil();
    const modal = new bootstrap.Modal(modalEl);
    cargarDatosPerfil();
    modal.show();
}

function cargarDatosPerfil() {
    const perfil = PerfilService.getPerfil() || PerfilService.getDefault();
    document.getElementById('perfil-nombre').value = perfil.nombre;
    document.getElementById('perfil-email').value = perfil.email;
    document.getElementById('perfil-telefono').value = perfil.telefono || '';
    document.getElementById('perfil-departamento').value = perfil.departamento || '';
    document.getElementById('perfil-puesto').value = perfil.puesto || '';
}

function guardarPerfil() {
    const perfil = {
        nombre: document.getElementById('perfil-nombre').value,
        email: document.getElementById('perfil-email').value,
        telefono: document.getElementById('perfil-telefono').value,
        departamento: document.getElementById('perfil-departamento').value,
        puesto: document.getElementById('perfil-puesto').value
    };

    PerfilService.save(perfil);
    
    const userData = JSON.parse(localStorage.getItem('userData'));
    userData.nombre = perfil.nombre;
    localStorage.setItem('userData', JSON.stringify(userData));
    
    bootstrap.Modal.getInstance(document.getElementById('modalPerfil')).hide();
    alert('Perfil guardado correctamente');
    window.location.reload();
}

function crearModalPerfil() {
    if (document.getElementById('modalPerfil')) return;
    
    const div = document.createElement('div');
    div.id = 'modalPerfil';
    div.className = 'modal fade';
    div.tabIndex = -1;
    div.innerHTML = `
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold">⚙️ Mi Perfil</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="form-perfil">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Nombre completo</label>
                                <input type="text" class="form-control" id="perfil-nombre">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="perfil-email" readonly>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Teléfono</label>
                                <input type="tel" class="form-control" id="perfil-telefono" placeholder="+52 ...">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Departamento</label>
                                <input type="text" class="form-control" id="perfil-departamento" placeholder="Ej. Ingeniería">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Puesto</label>
                            <input type="text" class="form-control" id="perfil-puesto" placeholder="Ej. Desarrollador Sr.">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="guardarPerfil()">Guardar Cambios</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(div);
    return div;
}