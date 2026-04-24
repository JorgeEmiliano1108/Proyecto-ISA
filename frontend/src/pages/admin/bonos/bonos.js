// --- SIMULACIÓN DE BACKEND (SERVICIOS) ---
// Centralizamos los datos para que sean fáciles de actualizar en el futuro
const BonosService = {
    async getResumenProgramas() {
        return {
            programa1: { 
                id: 'multiplicador',
                participantes: 142, 
                presupuesto: '64%', 
                desc: 'Cálculo del 15% del salario base anual basado en el cumplimiento trimestral de OKRs estratégicos para el nivel ejecutivo.' 
            },
            programa2: { 
                id: 'hito',
                lanzamiento: 'T3 2024', 
                responsabilidad: '$1.2M', 
                desc: 'Monto fijo de $25,000 pagados al completar 36 meses de antigüedad ininterrumpida como estrategia de retención de talento clave.' 
            },
            flujo: { 
                total: '$4.8M', 
                preparacion: 88, 
                totalEmpleados: 142 
            }
        };
    },
    async getAsignacionEmpleados() {
        return [
            { 
                id: 1, 
                nombre: 'Marcus Thorne', 
                puesto: 'Director de Operaciones', 
                programa: 'Multiplicador de Desempeño', 
                metodo: '15% SALARIO BASE', 
                estado: 'EN CURSO', 
                progreso: 92, 
                claseProgreso: 'bg-success', 
                pago: '$42,500' 
            },
            { 
                id: 2, 
                nombre: 'Elena Rodriguez', 
                puesto: 'Estrategia de Vicepresidencia', 
                programa: 'Hito de Retención', 
                metodo: 'FIJO: $25,000', 
                estado: 'TENURE PENDIENTE', 
                progreso: 60, 
                claseProgreso: 'bg-primary', 
                pago: '$25,000' 
            },
            { 
                id: 3, 
                nombre: 'Jonathan S.', 
                puesto: 'Arquitecto Principal', 
                programa: 'Multiplicador de Desempeño', 
                metodo: '10% SALARIO BASE', 
                estado: 'EN RIESGO', 
                progreso: 45, 
                claseProgreso: 'bg-danger', 
                pago: '$18,200' 
            }
        ];
    }
};

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
    }
});

// --- RENDERIZADO DE COMPONENTES ---

/**
 * Actualiza las tarjetas superiores y el flujo de caja
 */
function renderResumen(data) {
    // Programa 1: Multiplicador
    document.getElementById('participantes-1').textContent = data.programa1.participantes;
    document.getElementById('presupuesto-1').textContent = data.programa1.presupuesto;
    
    // Programa 2: Hito
    document.getElementById('lanzamiento-2').textContent = data.programa2.lanzamiento;
    document.getElementById('responsabilidad-2').textContent = data.programa2.responsabilidad;
    
    // Flujo de Incentivos (Tarjeta Azul)
    document.getElementById('flujo-total').textContent = data.flujo.total;
    document.getElementById('preparacion-porcentaje').textContent = data.flujo.preparacion + '%';
    
    const barraFlujo = document.getElementById('preparacion-barra');
    barraFlujo.style.width = data.flujo.preparacion + '%';
    barraFlujo.setAttribute('aria-valuenow', data.flujo.preparacion);
    
    // Total de registros en el footer de la tabla
    document.getElementById('total-empleados').textContent = data.flujo.totalEmpleados;
}

/**
 * Genera las filas de la tabla de empleados
 */
function renderTabla(datos) {
    const contenedor = document.getElementById('tabla-empleados');
    if (!contenedor) return;

    contenedor.innerHTML = datos.map(empleado => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-secondary bg-opacity-25" style="width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                        <i class="bi bi-person-fill text-secondary"></i>
                    </div>
                    <div>
                        ${empleado.nombre}<br>
                        <span class="text-muted small fw-normal">${empleado.puesto}</span>
                    </div>
                </div>
            </td>
            <td><span class="fw-medium">${empleado.programa}</span></td>
            <td class="text-uppercase small text-muted">${empleado.metodo}</td>
            <td>
                 <div class="d-flex flex-column">
                    <span class="text-uppercase small ${empleado.claseProgreso.replace('bg-', 'text-')} fw-bold" style="font-size: 0.65rem;">
                        ${empleado.estado}
                    </span>
                    <div class="progress" style="height: 6px; width: 120px; margin-top: 4px;">
                        <div class="progress-bar ${empleado.claseProgreso}" role="progressbar" style="width: ${empleado.progreso}%" aria-valuenow="${empleado.progreso}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <span class="small text-muted mt-1" style="font-size: 0.7rem;">${empleado.progreso}% completado</span>
                 </div>
            </td>
            <td class="fw-bold fs-6">${empleado.pago}</td>
        </tr>
    `).join('');
}

// --- INTERACTIVIDAD DE MODALES ---

/**
 * Inyecta datos dinámicos en el modal de detalles y lo muestra
 * Sustituye a los antiguos alerts para una vista más profesional
 */
async function verDetalleBono(tipo) {
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
        titulo.innerText = "Multiplicador de Desempeño";
        icono.innerHTML = "📈";
        icono.className = "icon-circle bg-light-blue text-primary me-3";
        participantes.innerText = data.programa1.participantes;
        utilizacion.innerText = data.programa1.presupuesto;
        barra.style.width = data.programa1.presupuesto;
        barra.className = "progress-bar bg-primary progress-bar-striped progress-bar-animated";
        fecha.innerText = "30 Sep 2024";
        desc.innerText = data.programa1.desc;
        badge.innerText = "ACTIVO";
        badge.className = "badge bg-success-subtle text-success small";
    } else if (tipo === 'Hito') {
        titulo.innerText = "Hito de Retención";
        icono.innerHTML = "🎗️";
        icono.className = "icon-circle bg-light text-secondary me-3";
        participantes.innerText = "Por definir";
        utilizacion.innerText = "0%";
        barra.style.width = "0%";
        fecha.innerText = "T3 2024";
        desc.innerText = data.programa2.desc;
        badge.innerText = "PLANEADO";
        badge.className = "badge bg-secondary-subtle text-secondary small";
    }
    
    modal.show();
}

/**
 * Función de utilidad para el botón de "Publicar" en el modal de nuevo programa
 */
function guardarNuevoPrograma() {
    // Aquí iría la lógica para capturar los datos de los inputs del formulario
    alert("Procesando datos... El nuevo programa ha sido registrado en ISA Corporativo.");
    location.reload(); // Recargamos para simular la actualización
}