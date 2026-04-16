// --- SIMULACIÓN DE BACKEND (SERVICIOS) ---
const UsuariosService = {
    async getResumen() {
        // En el futuro: return fetch('api/usuarios/resumen').then(r => r.json());
        return { total: 1284, activos: 412 };
    },
    async getUsuarios(pagina = 1, porPagina = 10) {
        // En el futuro: return fetch(`api/usuarios?pagina=${pagina}&porPagina=${porPagina}`).then(r => r.json());
        // Simulando datos para la página 1
        return {
            total: 1284,
            paginaActual: pagina,
            porPagina: porPagina,
            data: [
                { id: 1, nombre: 'Sarah Jenkins', email: 'sarah.j@empresa.com', rol: 'Arquitecta Sr.', dept: 'Estrategia de Producto', estado: 'Activo', ultimoLogin: 'Hace 2 min', claseEstado: 'text-success' },
                { id: 2, nombre: 'Marcus Rhodes', email: 'm.rhodes@empresa.com', rol: 'Líder de Equipo', dept: 'Ingeniería', estado: 'Activo', ultimoLogin: 'Hace 1 hora', claseEstado: 'text-success' },
                { id: 3, nombre: 'Elena Lopez', email: 'e.lopez@empresa.com', rol: 'Controladora', dept: 'Operaciones', estado: 'Inactivo', ultimoLogin: 'Ayer', claseEstado: 'text-muted' },
                 // ... más datos simulados ...
            ]
        };
    },
    async eliminarUsuario(id) {
        console.log(`Eliminando usuario con ID: ${id}`);
        // return fetch(`api/usuarios/${id}`, { method: 'DELETE' });
        return { success: true };
    }
};

// --- LÓGICA DE INICIALIZACIÓN Y RENDERIZADO ---
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [resumen, usuariosPagina] = await Promise.all([
            UsuariosService.getResumen(),
            UsuariosService.getUsuarios(1) // Carga la primera página por defecto
        ]);

        renderResumen(resumen);
        renderTabla(usuariosPagina.data);
        renderPaginacion(usuariosPagina);
    } catch (error) {
        console.error("Error cargando datos de usuarios:", error);
    }
});

function renderResumen(data) {
    document.getElementById('kpi-total').textContent = data.total.toLocaleString();
    document.getElementById('kpi-activos').textContent = data.activos;
    // También actualizamos el total en la tabla
    document.getElementById('total-usuarios-tabla').textContent = data.total.toLocaleString();
}

function renderTabla(datos) {
    const contenedor = document.getElementById('tabla-usuarios');
    contenedor.innerHTML = datos.map(user => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-dark" style="width: 32px; height: 32px;"></div>
                    <div>
                        ${user.nombre}<br>
                        <span class="text-muted small">${user.email}</span>
                    </div>
                </div>
            </td>
            <td><span class="badge bg-light text-secondary border text-uppercase small">${user.rol}</span></td>
            <td>${user.dept}</td>
            <td class="${user.claseEstado} fw-bold">• ${user.estado}</td>
            <td class="text-muted">${user.ultimoLogin}</td>
            <td>
                <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-light border" onclick="editarUsuario(${user.id})">✏️ Editar</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="borrarUsuario(${user.id})">🗑️ Borrar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderPaginacion(info) {
    const contenedor = document.getElementById('paginacion-usuarios');
    const totalPaginas = Math.ceil(info.total / info.porPagina);
    
    // Simplificación de paginación
    let html = `
        <li class="page-item ${info.paginaActual === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" aria-label="Anterior">
                <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
        <li class="page-item active"><a class="page-link" href="#">1</a></li>
        <li class="page-item"><a class="page-link" href="#">2</a></li>
        <li class="page-item"><a class="page-link" href="#">3</a></li>
        <li class="page-item disabled"><span class="page-link">...</span></li>
        <li class="page-item"><a class="page-link" href="#">12</a></li>
        <li class="page-item ${info.paginaActual === totalPaginas ? 'disabled' : ''}">
            <a class="page-link" href="#" aria-label="Siguiente">
                <span aria-hidden="true">&raquo;</span>
            </a>
        </li>
    `;
    
    contenedor.innerHTML = html;
}

// --- ACCIONES DE CRUD (FRONTEND) ---
function editarUsuario(id) {
    alert(`Abriendo modal de edición para el usuario ${id}. (Aquí iría el modal con el formulario)`);
    // En el futuro: cargar modal con datos del usuario.
}

async function borrarUsuario(id) {
    if (confirm(`¿Estás seguro de que quieres borrar el usuario ${id}? Esta acción no se puede deshacer.`)) {
        const res = await UsuariosService.eliminarUsuario(id);
        if (res.success) {
            alert("Usuario eliminado con éxito. Recargando tabla...");
            // Volver a cargar la página actual de la tabla.
            const usuariosPagina = await UsuariosService.getUsuarios(1);
            renderTabla(usuariosPagina.data);
        }
    }
}