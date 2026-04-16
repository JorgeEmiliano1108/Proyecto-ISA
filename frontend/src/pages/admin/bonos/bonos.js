// --- SIMULACIÓN DE BACKEND (SERVICIOS) ---
const BonosService = {
    async getResumenProgramas() {
        return {
            programa1: { participantes: 142, presupuesto: '64%' },
            programa2: { lanzamiento: 'T3 2024', responsabilidad: '$1.2M' },
            flujo: { total: '$4.8M', preparacion: 88, totalEmpleados: 142 }
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

// --- LÓGICA DE INICIALIZACIÓN Y RENDERIZADO ---
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [resumen, empleados] = await Promise.all([
            BonosService.getResumenProgramas(),
            BonosService.getAsignacionEmpleados()
        ]);

        renderResumen(resumen);
        renderTabla(empleados);
    } catch (error) {
        console.error("Error cargando datos de bonos:", error);
    }
});

function renderResumen(data) {
    document.getElementById('participantes-1').textContent = data.programa1.participantes;
    document.getElementById('presupuesto-1').textContent = data.programa1.presupuesto;
    document.getElementById('lanzamiento-2').textContent = data.programa2.lanzamiento;
    document.getElementById('responsabilidad-2').textContent = data.programa2.responsabilidad;
    document.getElementById('flujo-total').textContent = data.flujo.total;
    document.getElementById('preparacion-porcentaje').textContent = data.flujo.preparacion + '%';
    document.getElementById('preparacion-barra').style.width = data.flujo.preparacion + '%';
    document.getElementById('preparacion-barra').setAttribute('aria-valuenow', data.flujo.preparacion);
    document.getElementById('total-empleados').textContent = data.flujo.totalEmpleados;
}

function renderTabla(datos) {
    const contenedor = document.getElementById('tabla-empleados');
    contenedor.innerHTML = datos.map(empleado => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-circle bg-dark" style="width: 32px; height: 32px;"></div>
                    <div>
                        ${empleado.nombre}<br>
                        <span class="text-muted small">${empleado.puesto}</span>
                    </div>
                </div>
            </td>
            <td>${empleado.programa}</td>
            <td class="text-uppercase small text-muted">${empleado.metodo}</td>
            <td>
                 <span class="text-uppercase small ${empleado.claseProgreso.replace('bg-', 'text-')} fw-bold">${empleado.estado}</span>
                 <div class="progress" style="height: 6px;">
                    <div class="progress-bar ${empleado.claseProgreso}" role="progressbar" style="width: ${empleado.progreso}%" aria-valuenow="${empleado.progreso}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                 <span class="small text-muted">${empleado.progreso}%</span>
            </td>
            <td class="fw-bold fs-6">${empleado.pago}</td>
        </tr>
    `).join('');
}