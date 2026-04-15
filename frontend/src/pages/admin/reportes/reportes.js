// --- CONFIGURACIÓN DE COLORES ISA ---
const ISA_COLORS = {
    primary: '#0d6efd',
    lightBlue: '#eef4ff',
    warning: '#ffc107',
    success: '#198754'
};

// --- SIMULACIÓN DE BACKEND (SERVICIOS) ---
const ReportesService = {
    async getKpis() {
        return { total: 2842, promedio: 4.85, tasa: '98.2%', registros: 2842 };
    },
    async getTendenciasMensuales() {
        return {
            meses: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN'],
            volumen: [180, 250, 210, 480, 320, 550]
        };
    },
    async getEficienciaDepartamental() {
        return {
            departamentos: ['Ingeniería', 'Marketing', 'Recursos Humanos', 'Operaciones'],
            puntuaciones: [4.9, 4.7, 4.2, 4.5]
        };
    },
    async getTablaDetallada() {
        return [
            { id: 101, nombre: 'Juliana Sterling', dept: 'Ingeniería', fecha: 'Oct 24, 2023', score: 4.92, status: 'Aprobado', colorStatus: 'bg-success-subtle text-success' },
            { id: 102, nombre: 'Marcus Aurelius', dept: 'Operaciones', fecha: 'Oct 22, 2023', score: 3.80, status: 'Pendiente', colorStatus: 'bg-warning-subtle text-warning' },
            { id: 103, nombre: 'Lydia Bennet', dept: 'Recursos Humanos', fecha: 'Oct 21, 2023', score: 4.15, status: 'Aprobado', colorStatus: 'bg-success-subtle text-success' }
        ];
    }
};

// --- INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Obtenemos los datos (Backend Ready)
        const [kpis, tendencias, departamentos, tabla] = await Promise.all([
            ReportesService.getKpis(),
            ReportesService.getTendenciasMensuales(),
            ReportesService.getEficienciaDepartamental(),
            ReportesService.getTablaDetallada()
        ]);

        // Pintamos todo en español
        renderKpis(kpis);
        renderTabla(tabla);
        inicializarGraficaTendencias(tendencias);
        inicializarGraficaDepartamentos(departamentos);

    } catch (error) {
        console.error("Error al cargar analíticas:", error);
    }
});

// --- FUNCIONES DE RENDER (FRONTEND) ---
function renderKpis(data) {
    document.getElementById('kpi-total').textContent = data.total.toLocaleString();
    document.getElementById('kpi-promedio').textContent = data.promedio.toFixed(2);
    document.getElementById('kpi-tasa').textContent = data.tasa;
    document.getElementById('total-registros').textContent = data.registros.toLocaleString();
}

function renderTabla(datos) {
    const contenedor = document.getElementById('tabla-registros');
    contenedor.innerHTML = datos.map(row => `
        <tr class="align-middle">
            <td class="fw-bold text-dark-blue">${row.nombre}</td>
            <td class="text-secondary">${row.dept}</td>
            <td class="text-secondary">${row.fecha}</td>
            <td class="fw-bold fs-6">${row.score.toFixed(2)}</td>
            <td><span class="badge ${row.colorStatus} rounded-pill px-3">${row.status}</span></td>
            <td>
                <button class="btn btn-sm btn-light border text-primary fw-medium">
                    <i class="bi bi-eye me-1"></i> Ver
                </button>
            </td>
        </tr>
    `).join('');
}

// --- CONFIGURACIÓN DE GRÁFICAS (CHART.JS) ---
function inicializarGraficaTendencias(data) {
    const ctx = document.getElementById('chart-tendencias').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.meses,
            datasets: [{
                label: 'Volumen de Evaluaciones',
                data: data.volumen,
                backgroundColor: ISA_COLORS.lightBlue,
                borderColor: ISA_COLORS.primary,
                fill: true,
                tension: 0.4 // Suaviza la línea
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f0f0f0' } }
            }
        }
    });
}

function inicializarGraficaDepartamentos(data) {
    const ctx = document.getElementById('chart-departamentos').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.departamentos,
            datasets: [{
                label: 'Puntuación Promedio',
                data: data.puntuaciones,
                backgroundColor: ISA_COLORS.primary,
                borderRadius: 8 // Borde redondeado según el diseño
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 5.0 }
            }
        }
    });
}