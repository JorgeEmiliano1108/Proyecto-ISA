// --- DATOS GLOBALES (Simulación de base de datos) ---
let todasLasSolicitudes = [];
let todoElHistorial = [];

const SolicitudesService = {
    async getPendientes() {
        return [
            {
                id: 1,
                tipo: 'EVALUACIÓN',
                titulo: 'Evaluación de Desempeño Trimestral',
                solicitante: 'Sarah Jenkins',
                puesto: 'ARQUITECTA CLOUD SENIOR',
                fecha: '24 Oct, 2023',
                resumen: "Superó todos los KPIs para el Q3 incluyendo migración de infraestructura y metas de mentoría de equipo. Recomendada para calificación 'Excepcional' por su líder directo.",
                monto: 'N/A',
                icono: 'bi-ui-checks',
                colorIcono: 'text-primary',
                bgIcono: 'bg-light-blue',
                badgeColor: 'bg-light-blue text-primary'
            },
            {
                id: 2,
                tipo: 'BONO',
                titulo: 'Bono de Desempeño Anual',
                solicitante: 'Marcus Thorne',
                puesto: 'GERENTE DE OPERACIONES',
                fecha: '23 Oct, 2023',
                resumen: 'Propuesto para bono excepcional por cumplimiento de metas anuales.',
                monto: '$5,000 MXN',
                icono: 'bi-cash-stack',
                colorIcono: 'text-success',
                bgIcono: 'bg-light-green',
                badgeColor: 'bg-light-green text-success'
            },
            {
                id: 3,
                tipo: 'ACTUALIZACIÓN',
                titulo: 'Elevación de Acceso a Admin del Sistema',
                solicitante: 'Elena Rodriguez',
                puesto: 'ADMINISTRADORA DE SISTEMAS',
                fecha: '22 Oct, 2023',
                resumen: 'Solicita elevación temporal a administrador para mantenimiento de servidores.',
                monto: 'N/A',
                icono: 'bi-person-gear',
                colorIcono: 'text-secondary',
                bgIcono: 'bg-light',
                badgeColor: 'bg-light text-secondary'
            }
        ];
    },
    async getHistorial() {
        return [
            { entidad: 'Bono de Lanzamiento de Producto', tipo: 'BONO', accion: 'Pago Financiero', fecha: '21 Oct, 2023', resultado: 'APROBADO', statusClass: 'pill-approved', aprobador: 'Alex Mercer' },
            { entidad: 'Acceso Remoto VPN', tipo: 'ACTUALIZACIÓN', accion: 'Política de Seguridad', fecha: '20 Oct, 2023', resultado: 'RECHAZADO', statusClass: 'pill-denied', aprobador: 'Alex Mercer' },
            { entidad: 'Expansión de Equipo Dev', tipo: 'ACTUALIZACIÓN', accion: 'Asignación de Recursos', fecha: '19 Oct, 2023', resultado: 'APROBADO', statusClass: 'pill-approved', aprobador: 'Alex Mercer' }
        ];
    }
};

// --- INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", async () => {
    // Carga inicial de datos
    todasLasSolicitudes = await SolicitudesService.getPendientes();
    todoElHistorial = await SolicitudesService.getHistorial();
    
    // Mostramos todo por defecto
    filtrarSolicitudes('TODAS');
});

// --- LÓGICA DE FILTRADO ---
function filtrarSolicitudes(categoria, event) {
    if (event) event.preventDefault();

    // 1. Gestionar estado visual de las pestañas
    document.querySelectorAll('.filter-link').forEach(link => link.classList.remove('active'));
    
    if (event) {
        event.target.classList.add('active');
    } else {
        document.getElementById('filter-all').classList.add('active');
    }

    // 2. Filtrar y Renderizar Solicitudes Pendientes
    const solicitudesFiltradas = categoria === 'TODAS' 
        ? todasLasSolicitudes 
        : todasLasSolicitudes.filter(s => s.tipo === categoria);
    
    renderizarLista(solicitudesFiltradas);

    // 3. Filtrar y Renderizar Historial
    const historialFiltrado = categoria === 'TODAS'
        ? todoElHistorial
        : todoElHistorial.filter(h => h.tipo === categoria);
    
    renderizarHistorial(historialFiltrado);

    // 4. Actualizar el panel de "Revisión Rápida"
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

// --- RENDERIZADO DE COMPONENTES ---

function renderizarLista(items) {
    const contenedor = document.getElementById('lista-solicitudes');
    contenedor.innerHTML = items.map(item => `
        <div class="card border-0 shadow-sm mb-3 p-4 card-solicitud" onclick="verDetalle(${item.id})">
            <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center flex-grow-1">
                    <div class="icon-box me-4 ${item.bgIcono} ${item.colorIcono}">
                        <i class="bi ${item.icono}"></i>
                    </div>
                    <div>
                        <h6 class="fw-bold mb-1 text-dark-blue fs-5">${item.titulo}</h6>
                        <small class="text-muted"><i class="bi bi-person-fill me-1"></i> Solicitado por: <strong class="text-dark">${item.solicitante}</strong></small>
                    </div>
                </div>
                <div class="d-flex flex-column align-items-end gap-2">
                    <span class="badge ${item.badgeColor} border-0 px-2 py-1 text-uppercase" style="font-size: 0.65rem; letter-spacing: 0.5px;">${item.tipo}</span>
                    <small class="text-muted"><i class="bi bi-calendar3 me-1"></i> ${item.fecha}</small>
                </div>
            </div>
        </div>
    `).join('');
}

function verDetalle(id) {
    const item = todasLasSolicitudes.find(s => s.id === id);
    if (!item) return;
    
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
        
        <div class="card border-0 mb-3 p-3 shadow-sm bg-white" style="border-radius: 10px;">
            <label class="small text-muted text-uppercase mb-1" style="font-size: 0.65rem; letter-spacing: 0.5px;">Resumen</label>
            <p class="small text-muted mb-0 lh-sm">${item.resumen}</p>
        </div>
        
        <div class="card border-0 mb-3 p-3 shadow-sm bg-white" style="border-radius: 10px;">
            <label class="small text-muted text-uppercase mb-1" style="font-size: 0.65rem; letter-spacing: 0.5px;">Monto Solicitado (Opcional)</label>
            <p class="text-success fw-bold mb-0">${item.monto}</p>
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
            <td class="py-3 text-secondary">${item.fecha}</td>
            <td class="py-3">
                <span class="badge ${item.statusClass} px-3 py-2 text-uppercase" style="font-size: 0.65rem; letter-spacing: 0.5px;">${item.resultado}</span>
            </td>
            <td class="py-3 px-4 fw-bold text-dark-blue">${item.aprobador}</td>
        </tr>
    `).join('');
}

// --- LÓGICA DE ACCIONES (APROBAR/RECHAZAR) ---

// Función para procesar la acción
async function procesarAccion(esAprobado) {
    const detalleContenedor = document.getElementById('detalle-revision');
    const tituloSolicitud = detalleContenedor.querySelector('p.fw-bold')?.innerText;
    const nombreSolicitante = detalleContenedor.querySelector('h6.fw-bold')?.innerText;

    if (!tituloSolicitud) {
        alert("Por favor, selecciona una solicitud primero.");
        return;
    }

    const accion = esAprobado ? "APROBAR" : "RECHAZAR";
    const confirmacion = confirm(`¿Estás seguro de que deseas ${accion} la solicitud de ${nombreSolicitante}?`);

    if (confirmacion) {
        // Simulamos la llamada al servidor de ISA Corporativo
        console.log(`Enviando decisión a Auditoría: ${accion} - ${tituloSolicitud}`);
        
        // Efecto visual de carga en el botón
        const btnId = esAprobado ? 'btn-confirmar' : 'btn-rechazar';
        const btnOriginalText = document.getElementById(btnId).innerText;
        document.getElementById(btnId).innerText = "Procesando...";
        document.getElementById(btnId).disabled = true;

        // Simulamos un retraso de red
        setTimeout(() => {
            alert(`Solicitud de "${tituloSolicitud}" ha sido ${esAprobado ? 'APROBADA' : 'RECHAZADA'} con éxito.\nLa acción se ha registrado en la auditoría del sistema.`);
            
            // Restauramos el botón
            document.getElementById(btnId).innerText = btnOriginalText;
            document.getElementById(btnId).disabled = false;

            // Aquí podrías recargar la lista o quitar el elemento, 
            // por ahora solo notificamos como en el módulo de Publicar.
        }, 1000);
    }
}

// Asignación de eventos a los botones existentes
document.getElementById('btn-confirmar').addEventListener('click', () => procesarAccion(true));
document.getElementById('btn-rechazar').addEventListener('click', () => procesarAccion(false));