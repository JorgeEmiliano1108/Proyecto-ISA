const UsuariosService = {
    async getUsuarios() {
        const res = await apiFetch('/users/');
        if (!res.ok) return [];
        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.results || []);
        return list.map(u => ({
            id: u.id,
            nombre: u.nombre_completo || u.username,
            username: u.username,
            email: u.username + '@isa.com.mx',
            rol: u.puesto || '—',
            dept: u.departamento || '—',
            estado: u.activo === false ? 'Inactivo' : 'Activo',
            ultimoLogin: u.fecha_registro ? new Date(u.fecha_registro).toLocaleDateString('es-MX') : '—',
            claseEstado: u.activo === false ? 'text-muted' : 'text-success'
        }));
    },

    async eliminarUsuario(id) {
        const res = await apiFetch(`/users/${id}/`, { method: 'DELETE' });
        if (!res.ok) throw new Error('No se pudo eliminar');
        return { success: true };
    },

    async guardarUsuario(datos) {
        const method = datos.id ? 'PUT' : 'POST';
        const url = datos.id ? `/users/${datos.id}/` : '/users/';
        const res = await apiFetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(Object.values(err).flat().join(', ') || 'Error al guardar');
        }
        return { success: true };
    }
};

let modalUsuario;
let editando = false;
let usuarioIdActual = null;
let listaUsuariosLocal = [];

document.addEventListener("DOMContentLoaded", async () => {
    modalUsuario = new bootstrap.Modal(document.getElementById('modalUsuario'));

    try {
        listaUsuariosLocal = await UsuariosService.getUsuarios();
        renderResumen(listaUsuariosLocal);
        renderTabla(listaUsuariosLocal);
    } catch (error) {
        console.error("Error cargando usuarios:", error);
    }

    setupEventListeners();
});

function setupEventListeners() {
    const btnCrear = document.getElementById('btn-crear-usuario');
    const formUsuario = document.getElementById('form-usuario');
    const inputBusqueda = document.getElementById('input-busqueda');
    const btnExportar = document.getElementById('btn-exportar');

    inputBusqueda.addEventListener('input', (e) => {
        const termino = e.target.value.toLowerCase();
        const filtrados = listaUsuariosLocal.filter(user =>
            user.nombre.toLowerCase().includes(termino) ||
            user.email.toLowerCase().includes(termino) ||
            user.rol.toLowerCase().includes(termino)
        );
        renderTabla(filtrados);
    });

    btnExportar.addEventListener('click', () => {
        const csv = listaUsuariosLocal.map(u => `${u.nombre},${u.email},${u.rol},${u.dept},${u.estado}`).join('\n');
        const blob = new Blob(['Usuario,Email,Rol,Depto,Estado\n' + csv], { type: 'text/csv' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'usuarios.csv';
        a.click();
    });

    btnCrear.addEventListener('click', () => {
        editando = false;
        formUsuario.reset();
        document.getElementById('modalUsuarioLabel').textContent = "Nuevo Usuario";
        modalUsuario.show();
    });

    formUsuario.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        const datos = {
            id: editando ? usuarioIdActual : null,
            username: document.getElementById('email').value.split('@')[0],
            nombre_completo: document.getElementById('nombre').value,
            puesto: document.getElementById('rol').value,
            password: 'temporal123'
        };

        try {
            await UsuariosService.guardarUsuario(datos);
            listaUsuariosLocal = await UsuariosService.getUsuarios();
            modalUsuario.hide();
            renderTabla(listaUsuariosLocal);
            renderResumen(listaUsuariosLocal);
        } catch (error) {
            alert('Error: ' + error.message);
        }
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
                <button class="btn btn-sm btn-light border" onclick="editarUsuario('${user.id}')">✏️</button>
                <button class="btn btn-sm btn-outline-danger" onclick="borrarUsuario('${user.id}')">🗑️</button>
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
        document.getElementById('modalUsuarioLabel').textContent = "Editar Usuario";
        modalUsuario.show();
    }
}

async function borrarUsuario(id) {
    if (!confirm("¿Eliminar usuario?")) return;
    try {
        await UsuariosService.eliminarUsuario(id);
        listaUsuariosLocal = listaUsuariosLocal.filter(u => u.id !== id);
        renderTabla(listaUsuariosLocal);
        renderResumen(listaUsuariosLocal);
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function renderResumen(data) {
    const total = data.length || 0;
    document.getElementById('kpi-total').textContent = total;
    document.getElementById('kpi-activos').textContent = data.filter(u => u.estado === 'Activo').length;
    document.getElementById('total-usuarios-tabla').textContent = total;
}
