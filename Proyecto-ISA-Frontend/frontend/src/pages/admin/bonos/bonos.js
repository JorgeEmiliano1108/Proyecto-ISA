/**
 * SERVICIO DE BONOS - Capa de servicio para comunicación con API Django.
 * Reemplaza los mocks hardcodeados por llamadas reales a la API Django.
 */
import { BonosService } from '../../services/bonos.js';

// --- LÓGICA DE INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Ejecutamos ambas peticiones en paralelo para mayor velocidad
        const [resumen, empleados] = await Promise.all([
            BonosService.getResumenProgramas(),
            BonosService.getAsignacionEmpleados()
        ]);

        renderResumen(resumen);
        renderTabla(empleados);
    } catch (error) {
        console.error("Error al cargar la Arquitectura de Incentivos:", error);
        // Fallback a datos vacíos para no romper la UI
        renderResumen({ programa1: {}, programa2: {}, flujo: {} });
        renderTabla([]);
    }
});

// --- RENDERIZADO DE COMPONENTES ---

/**
 * Actualiza las tarjetas superiores y el flujo de caja
 */
function renderResumen(data) {
    // Programa 1: Multiplicador
    document.getElementById('participantes-1').textContent = data.programa1?.participantes || '...';
    document.getElementById('presupuesto-1').textContent = data.programa1?.presupuesto || '...';
    
    // Programa 2: Hito
    document.getElementById('lanzamiento-2').textContent = data.programa2?.lanzamiento || '...';
    document.getElementById('responsabilidad-2').textContent = data.programa2?.responsabilidad || '...';
    
    // Flujo de Incentivos (Tarjeta Azul)
    document.getElementById('flujo-total').textContent = data.flujo?.total || '...';
    document.getElementById('preparacion-porcentaje').textContent = data.flujo?.preparacion ? data.flujo.preparacion + '%' : '...';
    
    const barraFlujo = document.getElementById('preparacion-barra');
    if (barraFlujo) {
        barraFlujo.style.width = data.flujo?.preparacion ? data.flujo.preparacion + '%' : '0%';
        barraFlujo.setAttribute('aria-valuenow', data.flujo?.preparacion || 0);
    }
    
    // Total de registros en el footer de la tabla
    document.getElementById('total-empleados').textContent = data.flujo?.totalEmpleados || '...';
}

/**
 * Genera las filas de la tabla de empleados
 */
function renderTabla(datos) {
    const contenedor = document.getElementById('tabla-empleados');
    if (!contenedor) return;

    if (!datos || datos.length === 0) {
        contenedor.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    No hay empleados asignados a programas de bonos
                </td>
            </tr>
        `;
        return;
    }

    contenedor.innerHTML = datos.map(empleado => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-secondary bg-opacity-25" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                        <i class="bi bi-person-fill text-secondary"></i>
                    </div>
                    <div>
                        ${empleado.nombre || empleado.nombre_completo || 'Sin nombre'}<br>
                        <span class="text-muted small fw-normal">${empleado.puesto || 'Sin puesto'}</span>
                    </div>
                </div>
            </td>
            <td><span class="fw-medium">${empleado.programa || 'Sin programa'}</span></td>
            <td class="text-uppercase small text-muted">${empleado.metodo || 'Sin método'}</td>
            <td>
                 <div class="d-flex flex-column">
                    <span class="text-uppercase small ${(empleado.claseProgreso || 'bg-secondary').replace('bg-', 'text-')} fw-bold" style="font-size: 0.65rem;">
                        ${empleado.estado || 'SIN ESTADO'}
                    </span>
                    <div class="progress" style="height: 6px; width: 120px; margin-top: 4px;">
                        <div class="progress-bar ${empleado.claseProgreso || 'bg-secondary'}" role="progressbar" style="width: ${empleado.progreso || 0}%" aria-valuenow="${empleado.progreso || 0}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <span class="small text-muted mt-1" style="font-size: 0.7rem;">${empleado.progreso || 0}% completado</span>
                 </div>
            </td>
            <td class="fw-bold fs-6">${empleado.pago || '$0.00'}</td>
        </tr>
    `).join('');
}

// --- INTERACTIVIDAD DE MODALES ---

/**
 * Inyecta datos dinámicos en el modal de detalles y lo muestra
 * Sustituye a los antiguos alerts para una vista más profesional
 */
async function verDetalleBono(tipo) {
    try {
        const data = await BonosService.getResumenProgramas();
        const modalElement = document.getElementById('modalDetallePrograma');
        const modal = new bootstrap.Modal(modalElement);
        
        // Elementos del Modal para actualizar
        const titulo = document.getElementById('detalle-titulo');
        const icono = document.getElementById('detalle-icon');
        const participantes = document.getElementById('det-participantes');
        const utilizacion = document.getElementById('det-utilizacion');
        const barra = document.getElementById('det-barra');
        const fecha = document.getElementById('det-fecha');
        const desc = document.getElementById('detalle-desc');
        const badge = document.getElementById('detalle-estado');

        if(tipo === 'Multiplicador') {
            const prog = data.programa1 || {};
            titulo.innerText = "Multiplicador de Desempeño";
            icono.innerHTML = "📈";
            icono.className = "icon-circle bg-light-blue text-primary me-3";
            document.getElementById('det-participantes').innerText = prog.participantes || '...';
            document.getElementById('det-utilizacion').innerText = prog.presupuesto || '...';
            if (barra) {
                barra.style.width = prog.presupuesto || '0%';
                barra.className = "progress-bar bg-primary progress-bar-striped progress-bar-animated";
            }
            document.getElementById('det-fecha').innerText = "30 Sep 2024";
            document.getElementById('detalle-desc').innerText = prog.desc || 'Sin descripción';
            document.getElementById('detalle-estado').innerText = "ACTIVO";
            document.getElementById('detalle-estado').className = "badge bg-success-subtle text-success small";
        } else if (tipo === 'Hito') {
            const prog = data.programa2 || {};
            document.getElementById('detalle-titulo').innerText = "Hito de Retención";
            document.getElementById('detalle-icon').innerHTML = "🎗️";
            document.getElementById('detalle-icon').className = "icon-circle bg-light text-secondary me-3";
            document.getElementById('det-participantes').innerText = "Por definir";
            document.getElementById('det-utilizacion').innerText = "0%";
            const barra = document.getElementById('det-barra');
            if (barra) {
                barra.style.width = "0%";
                barra.className = "progress-bar progress-bar-striped progress-bar-animated";
            }
            document.getElementById('det-fecha').innerText = "T3 2024";
            const prog2 = data.programa2 || {};
            document.getElementById('detalle-desc').innerText = prog2.desc || 'Sin descripción';
            document.getElementById('detalle-estado').innerText = "PLANEADO";
            document.getElementById('detalle-estado').className = "badge bg-secondary-subtle text-secondary small";
        }
        
        const modal = new bootstrap.Modal(document.getElementById('modalDetallePrograma'));
        modal.show();
    } catch (error) {
        console.error("Error al cargar detalle del bono:", error);
        alert("Error al cargar los detalles del programa");
    }
}

/**
 * Función de utilidad para el botón de "Publicar" en el modal de nuevo programa
 */
async function guardarNuevoPrograma() {
    // Capturar datos del formulario del modal
    const modal = document.getElementById('modalNuevoBono');
    const form = modal.querySelector('form') || modal.querySelector('.modal-body');
    
    if (!form) {
        alert("Error: No se encontró el formulario");
        return;
    }

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Validar campos requeridos
    if (!data.nombre || !data.tipo_calculo || !data.valor || !data.fecha_inicio || !data.fecha_fin) {
        alert("Por favor complete todos los campos obligatorios");
        return;
    }

    try {
        // Llamar a la API para crear el programa
        const res = await fetch('/api/v1/finances/bonos/programas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                nombre: data.nombre,
                descripcion: data.descripcion || '',
                tipo_calculo: data.tipo_calculo,
                valor: parseFloat(data.valor),
                presupuesto_limite: data.presupuesto_limite ? parseFloat(data.presupuesto_limite) : null,
                fecha_inicio: data.fecha_inicio,
                fecha_fin: data.fecha_fin,
                estado: 'activo'
            })
        });

        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Error al crear programa');
        }

        // Cerrar modal y recargar
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoBono'));
        modal.hide();
        
        alert("Programa creado exitosamente");
        location.reload();
    } catch (error) {
        console.error("Error al crear programa:", error);
        alert("Error al crear el programa: " + error.message);
    }
}