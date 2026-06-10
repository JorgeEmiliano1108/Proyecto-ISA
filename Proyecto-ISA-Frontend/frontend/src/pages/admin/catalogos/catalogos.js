const CatalogosService = {
    async getCatalogo(endpoint) {
        try {
            const res = await apiFetch(`/catalogs/${endpoint}/`);
            if (!res.ok) return [];
            const data = await res.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch {
            return [];
        }
    },

    async getCompetencias() {
        return this.getCatalogo('competencias');
    },
    async getDepartamentos() {
        return this.getCatalogo('departamentos');
    },
    async getRoles() {
        return this.getCatalogo('roles');
    },
    async getPeriodos() {
        return this.getCatalogo('periodos');
    },

    async update(endpoint, id, data) {
        const res = await apiFetch(`/catalogs/${endpoint}/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(Object.values(err).flat().join(', ') || 'Error al guardar');
        }
        return await res.json();
    },

    async create(endpoint, data) {
        const res = await apiFetch(`/catalogs/${endpoint}/`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(Object.values(err).flat().join(', ') || 'Error al crear');
        }
        return await res.json();
    },

    async delete(endpoint, id) {
        const res = await apiFetch(`/catalogs/${endpoint}/${id}/`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Error al eliminar');
        return true;
    }
};

let catalogoActual = 'competencias';
let datosCatalogo = [];

const ICONOS = {
    competencias: 'bi-star',
    departamentos: 'bi-building',
    roles: 'bi-person-badge',
    periodos: 'bi-calendar-range'
};

const ETIQUETAS = {
    competencias: 'Competencias',
    departamentos: 'Departamentos',
    roles: 'Roles',
    periodos: 'Períodos'
};

const SUBTITULOS = {
    competencias: 'Catálogo de competencias del sistema',
    departamentos: 'Catálogo de departamentos y áreas',
    roles: 'Catálogo de roles y niveles de aprobación',
    periodos: 'Catálogo de períodos de evaluación'
};

const CAMPOS = {
    competencias: ['nombre', 'descripcion'],
    departamentos: ['nombre'],
    roles: ['nombre', 'nivel_aprobacion'],
    periodos: ['nombre']
};

const CABECERAS = {
    competencias: ['Nombre', 'Descripción'],
    departamentos: ['Nombre'],
    roles: ['Nombre', 'Nivel Aprobación'],
    periodos: ['Nombre']
};

document.addEventListener("DOMContentLoaded", async () => {
    await cargarCatalogo('competencias');
    renderCategorias();
    inicializarGrafica();
});

async function cargarCatalogo(tipo) {
    catalogoActual = tipo;
    document.getElementById('titulo-catalogo').textContent = ETIQUETAS[tipo] || tipo;
    document.getElementById('icono-catalogo').className = `bi ${ICONOS[tipo] || 'bi-folder'} fs-4`;
    document.getElementById('subtitulo-catalogo').textContent = SUBTITULOS[tipo] || '';

    try {
        datosCatalogo = await CatalogosService[`get${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`]();
    } catch {
        datosCatalogo = [];
    }

    document.getElementById('items-count').textContent = `${datosCatalogo.length} registros`;
    renderCatalogo(datosCatalogo);
    renderActividad(datosCatalogo);
    actualizarGrafica();
}

function renderCategorias() {
    const contenedor = document.getElementById('lista-categorias');
    contenedor.innerHTML = Object.keys(ETIQUETAS).map(key => `
        <button class="btn text-start w-100 p-3 rounded-3 d-flex align-items-center justify-content-between ${catalogoActual === key ? 'btn-primary text-white shadow-sm' : 'btn-light text-muted border-0'}"
                onclick="cambiarCatalogo('${key}')">
            <div class="d-flex align-items-center gap-3">
                <i class="bi ${ICONOS[key]} fs-5"></i>
                <span class="${catalogoActual === key ? 'fw-bold' : 'fw-medium'}">${ETIQUETAS[key]}</span>
            </div>
            ${catalogoActual === key ? '<i class="bi bi-chevron-right small"></i>' : ''}
        </button>
    `).join('');
}

window.cambiarCatalogo = async (tipo) => {
    await cargarCatalogo(tipo);
    renderCategorias();
};

function renderCatalogo(datos) {
    const contenedor = document.getElementById('estructura-menu');
    if (!datos || datos.length === 0) {
        contenedor.innerHTML = '<div class="text-center text-muted py-5"><i class="bi bi-inbox fs-1 d-block mb-2"></i>Sin datos</div>';
        return;
    }

    const campos = CAMPOS[catalogoActual];
    const cabeceras = CABECERAS[catalogoActual];

    let html = `<div class="table-responsive"><table class="table table-hover align-middle"><thead class="table-light text-muted small text-uppercase"><tr>`;
    cabeceras.forEach(c => { html += `<th>${c}</th>`; });
    html += `<th>Activo</th><th>Acción</th></tr></thead><tbody>`;

    datos.forEach(item => {
        html += `<tr class="align-middle">`;
        campos.forEach(campo => {
            const val = item[campo] || '—';
            html += `<td class="fw-medium">${val}</td>`;
        });
        html += `<td><span class="badge ${item.activo !== false ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'} rounded-pill">${item.activo !== false ? 'Activo' : 'Inactivo'}</span></td>`;
        html += `<td>
            <button class="btn btn-sm btn-outline-primary me-1" onclick="editarItem('${item.id}')" title="Editar"><i class="bi bi-pencil"></i></button>
            <button class="btn btn-sm btn-outline-danger" onclick="eliminarItem('${item.id}')" title="Eliminar"><i class="bi bi-trash"></i></button>
        </td>`;
        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    contenedor.innerHTML = html;
}

function itemActual() {
    return datosCatalogo.find(i => i.id === itemEditandoId);
}

let itemEditandoId = null;
const CAMPOS_MODAL = {
    competencias: [
        { id: 'campo-nombre', label: 'Nombre', type: 'text', campo: 'nombre' },
        { id: 'campo-descripcion', label: 'Descripción', type: 'textarea', campo: 'descripcion' }
    ],
    departamentos: [
        { id: 'campo-nombre', label: 'Nombre', type: 'text', campo: 'nombre' }
    ],
    roles: [
        { id: 'campo-nombre', label: 'Nombre', type: 'text', campo: 'nombre' },
        { id: 'campo-nivel', label: 'Nivel Aprobación', type: 'number', campo: 'nivel_aprobacion' }
    ],
    periodos: [
        { id: 'campo-nombre', label: 'Nombre', type: 'text', campo: 'nombre' }
    ]
};

window.editarItem = function(id) {
    itemEditandoId = id;
    const item = itemActual();
    if (!item) return;

    const campos = CAMPOS_MODAL[catalogoActual];
    document.getElementById('modal-titulo').textContent = `Editar ${ETIQUETAS[catalogoActual]}`;
    document.getElementById('campos-dinamicos').innerHTML = campos.map(c => `
        <div class="mb-3">
            <label class="form-label fw-medium">${c.label}</label>
            ${c.type === 'textarea'
                ? `<textarea class="form-control" id="${c.id}" rows="3">${item[c.campo] || ''}</textarea>`
                : `<input type="${c.type}" class="form-control" id="${c.id}" value="${item[c.campo] || ''}">`
            }
        </div>
    `).join('');

    document.getElementById('campo-activo').value = item.activo !== false ? 'true' : 'false';

    new bootstrap.Modal(document.getElementById('modalEditarCatalogo')).show();
};

window.guardarEdicion = async function() {
    const item = itemActual();
    if (!item) return;

    const campos = CAMPOS_MODAL[catalogoActual];
    const data = {};
    campos.forEach(c => {
        const el = document.getElementById(c.id);
        data[c.campo] = c.type === 'number' ? parseInt(el.value) || 0 : el.value;
    });
    data.activo = document.getElementById('campo-activo').value === 'true';

    try {
        await CatalogosService.update(catalogoActual, itemEditandoId, data);
        bootstrap.Modal.getInstance(document.getElementById('modalEditarCatalogo')).hide();
        await cargarCatalogo(catalogoActual);
    } catch (error) {
        alert('Error: ' + error.message);
    }
};

window.eliminarItem = async function(id) {
    if (!confirm('¿Eliminar este registro?')) return;
    try {
        await CatalogosService.delete(catalogoActual, id);
        await cargarCatalogo(catalogoActual);
    } catch (error) {
        alert('Error: ' + error.message);
    }
};

function renderActividad(datos) {
    const contenedor = document.getElementById('lista-actividad');
    if (!datos || datos.length === 0) {
        contenedor.innerHTML = '<div class="text-muted small text-center py-3">Sin registros</div>';
        return;
    }
    contenedor.innerHTML = datos.slice(0, 5).map(item => `
        <div class="d-flex gap-3">
            <div class="mt-1"><i class="bi bi-circle-fill text-primary" style="font-size: 0.5rem;"></i></div>
            <div>
                <p class="small mb-1"><strong class="text-dark">${item.nombre || item.id}</strong></p>
                <small class="text-primary" style="font-size: 0.65rem;">${item.activo !== false ? 'Activo' : 'Inactivo'}</small>
            </div>
        </div>
    `).join('');
}

let chartInstancia = null;

async function inicializarGrafica() {
    const canvas = document.getElementById('chart-navegacion');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = Object.values(ETIQUETAS);
    const valores = await Promise.all(
        Object.keys(ETIQUETAS).map(async key => {
            const data = await CatalogosService[`get${key.charAt(0).toUpperCase() + key.slice(1)}`]();
            return data.length;
        })
    );

    chartInstancia = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: '#cddbfe',
                hoverBackgroundColor: '#8baffc',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

async function actualizarGrafica() {
    if (!chartInstancia) return;
    const valores = await Promise.all(
        Object.keys(ETIQUETAS).map(async key => {
            const data = await CatalogosService[`get${key.charAt(0).toUpperCase() + key.slice(1)}`]();
            return data.length;
        })
    );
    chartInstancia.data.datasets[0].data = valores;
    chartInstancia.update();
}
