/**
 * SERVICIO DE CATÁLOGOS (Simulación de Backend)
 */
const CatalogosService = {
    async getCategorias() {
        return [
            { id: 1, nombre: "Menú de Navegación", icono: "bi-diagram-3", activo: true },
            { id: 2, nombre: "Constantes del Sistema", icono: "bi-database", activo: false },
            { id: 3, nombre: "Valores Desplegables", icono: "bi-list-ul", activo: false },
            { id: 4, nombre: "Datos Geográficos", icono: "bi-globe-americas", activo: false }
        ];
    },

    async getEstructuraMenu() {
        // Simulación de una estructura de árbol (JSON)
        return [
            { id: 'NAV_DASHBOARD_MAIN', titulo: 'Dashboard', icono: 'bi-grid-1x2', estado: 'VISIBLE', badgeClass: 'bg-success-subtle text-success' },
            { id: 'NAV_ANALYTICS_GRP', titulo: 'Analítica de Desempeño', icono: 'bi-bar-chart', estado: 'VISIBLE', badgeClass: 'bg-success-subtle text-success', subitems: [
                { titulo: 'Métricas de Crecimiento', icono: 'bi-graph-up' },
                { titulo: 'Asignación de Recursos', icono: 'bi-pie-chart' }
            ]},
            { id: 'NAV_CATALOG_ADMIN', titulo: 'Gestión de Catálogos', icono: 'bi-folder2-open', estado: 'BLOQUEADO', badgeClass: 'bg-secondary-subtle text-secondary' },
            { id: 'NAV_BETA_EXP', titulo: 'Funciones Beta', icono: 'bi-flask', estado: 'OCULTO', badgeClass: 'bg-danger-subtle text-danger' }
        ];
    },

    async getActividad() {
        return [
            { usuario: "Marcus V.", accion: "modificó el Menú", detalle: 'Cambió el orden de "Analítica" a la pos 2', tiempo: "12:45 PM HOY", color: "text-primary" },
            { usuario: "Sincronización de Sistema", accion: "Completada", detalle: 'Esquema V2.4.1 enviado a Producción', tiempo: "09:12 AM HOY", color: "text-success" }
        ];
    }
};

/**
 * CONTROLADOR E INICIALIZACIÓN
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [categorias, menu, actividad] = await Promise.all([
            CatalogosService.getCategorias(),
            CatalogosService.getEstructuraMenu(),
            CatalogosService.getActividad()
        ]);

        renderCategorias(categorias);
        renderEstructuraMenu(menu);
        renderActividad(actividad);
        inicializarGrafica(); // Gráfica inferior
    } catch (error) {
        console.error("Error cargando datos de catálogos:", error);
    }
});

// -- Funciones de Renderizado --

function renderCategorias(categorias) {
    const contenedor = document.getElementById('lista-categorias');
    contenedor.innerHTML = categorias.map(cat => `
        <button class="btn text-start w-100 p-3 rounded-3 d-flex align-items-center justify-content-between ${cat.activo ? 'btn-primary text-white shadow-sm' : 'btn-light text-muted border-0'}">
            <div class="d-flex align-items-center gap-3">
                <i class="bi ${cat.icono} fs-5"></i>
                <span class="${cat.activo ? 'fw-bold' : 'fw-medium'}">${cat.nombre}</span>
            </div>
            ${cat.activo ? '<i class="bi bi-chevron-right small"></i>' : ''}
        </button>
    `).join('');
}

function renderEstructuraMenu(items) {
    const contenedor = document.getElementById('estructura-menu');
    let html = '';

    items.forEach(item => {
        // Tarjeta Principal
        html += `
        <div class="menu-item-row bg-white border rounded-3 p-3 d-flex justify-content-between align-items-center shadow-sm mb-1">
            <div class="d-flex align-items-center gap-3">
                <i class="bi bi-grip-vertical text-muted drag-handle"></i>
                <div class="icon-square-sm bg-light text-dark rounded"><i class="bi ${item.icono}"></i></div>
                <div>
                    <h6 class="fw-bold mb-0 text-dark-blue">${item.titulo} ${item.subitems ? '<i class="bi bi-chevron-down small ms-1 text-muted"></i>' : ''}</h6>
                    <small class="text-muted" style="font-size: 0.7rem; font-family: monospace;">ID: ${item.id}</small>
                </div>
            </div>
            <div class="d-flex align-items-center gap-3">
                <span class="badge ${item.badgeClass} rounded-pill px-3 py-1" style="font-size: 0.7rem;">${item.estado}</span>
                <button class="btn btn-sm btn-link text-muted"><i class="bi bi-pencil"></i></button>
            </div>
        </div>
        `;

        // Sub-items (Si existen)
        if (item.subitems) {
            html += `<div class="ms-5 d-flex flex-column gap-1 mb-2 border-start border-2 ps-3">`;
            item.subitems.forEach(sub => {
                html += `
                <div class="d-flex justify-content-between align-items-center p-2 rounded hover-bg-light">
                    <div class="d-flex align-items-center gap-3 text-muted">
                        <i class="bi bi-grip-vertical drag-handle-sm"></i>
                        <i class="bi ${sub.icono} small"></i>
                        <span class="small fw-medium">${sub.titulo}</span>
                    </div>
                    <i class="bi bi-gear small text-muted"></i>
                </div>
                `;
            });
            // Botón de agregar sub-menú
            html += `
                <button class="btn btn-sm text-primary text-start border-dashed mt-1 p-2 rounded">
                    <i class="bi bi-plus-circle me-2"></i> Agregar Sub-menú
                </button>
            </div>`;
        }
    });

    contenedor.innerHTML = html;
}

function renderActividad(actividad) {
    const contenedor = document.getElementById('lista-actividad');
    contenedor.innerHTML = actividad.map(act => `
        <div class="d-flex gap-3">
            <div class="mt-1"><i class="bi bi-circle-fill ${act.color}" style="font-size: 0.5rem;"></i></div>
            <div>
                <p class="small mb-1"><strong class="text-dark">${act.usuario}</strong> <span class="text-muted">${act.accion}</span></p>
                <p class="smaller text-muted mb-1">${act.detalle}</p>
                <small class="text-primary" style="font-size: 0.65rem; font-weight: 600;">${act.tiempo}</small>
            </div>
        </div>
    `).join('');
}

function inicializarGrafica() {
    const ctx = document.getElementById('chart-navegacion').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom', 'Lun', 'Mar', 'Mié'],
            datasets: [{
                data: [30, 20, 45, 60, 40, 70, 85, 20, 25, 45],
                backgroundColor: '#cddbfe', // Azul muy claro
                hoverBackgroundColor: '#8baffc',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false }, // Ocultar ejes para que se vea minimalista como en tu foto
                y: { display: false }
            }
        }
    });
}