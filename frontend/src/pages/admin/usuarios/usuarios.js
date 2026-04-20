// --- SERVICIOS ---
const UsuariosService = {
    async getResumen() { return { total: 1284, activos: 412 }; },
    async getUsuarios() {
        return [
            { id: 1, nombre: 'Sarah Jenkins', email: 'sarah.j@empresa.com', rol: 'Arquitecta Sr.', dept: 'Estrategia de Producto', estado: 'Activo', ultimoLogin: 'Hace 2 min', claseEstado: 'text-success' },
            { id: 2, nombre: 'Marcus Rhodes', email: 'm.rhodes@empresa.com', rol: 'Líder de Equipo', dept: 'Ingeniería', estado: 'Activo', ultimoLogin: 'Hace 1 hora', claseEstado: 'text-success' },
            { id: 3, nombre: 'Elena Lopez', email: 'e.lopez@empresa.com', rol: 'Controladora', dept: 'Operaciones', estado: 'Inactivo', ultimoLogin: 'Ayer', claseEstado: 'text-muted' }
        ];
    },
    async eliminarUsuario(id) { console.log(`Eliminado: ${id}`); return { success: true }; },
    async guardarUsuario(datos) { console.log("Guardado:", datos); return { success: true }; }
};

// --- VARIABLES ---
let modalUsuario;
let editando = false;
let usuarioIdActual = null;
let listaUsuariosLocal = [];

document.addEventListener("DOMContentLoaded", async () => {
    modalUsuario = new bootstrap.Modal(document.getElementById('modalUsuario'));
    const resumen = await UsuariosService.getResumen();
    listaUsuariosLocal = await UsuariosService.getUsuarios();
    
    renderResumen(resumen);
    renderTabla(listaUsuariosLocal);
    setupEventListeners();
});

function setupEventListeners() {
    const btnCrear = document.getElementById('btn-crear-usuario');
    const formUsuario = document.getElementById('form-usuario');
    const inputBusqueda = document.getElementById('input-busqueda');
    const btnExportar = document.getElementById('btn-exportar');

    // FILTRO EN TIEMPO REAL
    inputBusqueda.addEventListener('input', (e) => {
        const termino = e.target.value.toLowerCase();
        const filtrados = listaUsuariosLocal.filter(user => 
            user.nombre.toLowerCase().includes(termino) || 
            user.email.toLowerCase().includes(termino)
        );
        renderTabla(filtrados);
    });

    // EXPORTAR (Simulado)
    btnExportar.addEventListener('click', () => alert("Descargando reporte de usuarios..."));

    btnCrear.addEventListener('click', () => {
        editando = false;
        formUsuario.reset();
        document.getElementById('modalUsuarioLabel').textContent = "➕ Nuevo Usuario";
        modalUsuario.show();
    });

    formUsuario.addEventListener('submit', async (e) => {
        e.preventDefault();
        const datos = {
            id: editando ? usuarioIdActual : Date.now(),
            nombre: document.getElementById('nombre').value,
            email: document.getElementById('email').value,
            rol: document.getElementById('rol').value,
            dept: document.getElementById('dept').value,
            estado: 'Activo', ultimoLogin: 'Ahora', claseEstado: 'text-success'
        };

        await UsuariosService.guardarUsuario(datos);
        if (editando) {
            const idx = listaUsuariosLocal.findIndex(u => u.id === usuarioIdActual);
            listaUsuariosLocal[idx] = datos;
        } else {
            listaUsuariosLocal.push(datos);
        }
        
        modalUsuario.hide();
        renderTabla(listaUsuariosLocal);
    });
}

function renderTabla(datos) {
    const contenedor = document.getElementById('tabla-usuarios');
    document.getElementById('mostrando-count').textContent = datos.length;
    
    contenedor.innerHTML = datos.map(user => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-secondary-subtle d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                        ${user.nombre.charAt(0)}
                    </div>
                    <div>${user.nombre}<br><span class="text-muted small">${user.email}</span></div>
                </div>
            </td>
            <td><span class="badge bg-light text-secondary border small">${user.rol}</span></td>
            <td>${user.dept}</td>
            <td class="${user.claseEstado} fw-bold small">• ${user.estado}</td>
            <td class="text-muted small">${user.ultimoLogin}</td>
            <td>
                <button class="btn btn-sm btn-light border" onclick="editarUsuario(${user.id})">✏️</button>
                <button class="btn btn-sm btn-outline-danger" onclick="borrarUsuario(${user.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function editarUsuario(id) {
    editando = true;
    usuarioIdActual = id;
    const user = listaUsuariosLocal.find(u => u.id === id);
    if (user) {
        document.getElementById('nombre').value = user.nombre;
        document.getElementById('email').value = user.email;
        document.getElementById('rol').value = user.rol;
        document.getElementById('dept').value = user.dept;
        document.getElementById('modalUsuarioLabel').textContent = "✏️ Editar Usuario";
        modalUsuario.show();
    }
}

async function borrarUsuario(id) {
    if (confirm("¿Eliminar usuario?")) {
        listaUsuariosLocal = listaUsuariosLocal.filter(u => u.id !== id);
        renderTabla(listaUsuariosLocal);
    }
}

function renderResumen(data) {
    document.getElementById('kpi-total').textContent = data.total.toLocaleString();
    document.getElementById('kpi-activos').textContent = data.activos;
    document.getElementById('total-usuarios-tabla').textContent = data.total.toLocaleString();
}