// --- CONFIGURACIÓN DE COLORES ISA ---
const ISA_COLORS = {
    primary: '#0d6efd',
    lightBlue: '#eef4ff',
    warning: '#ffc107',
    success: '#198754'
};

// Instancias de gráficas para poder destruirlas al actualizar
let chartTendencias = null;
let chartDept = null;

// --- SIMULACIÓN DE DATOS POR TEMPORALIDAD ---
const DatosPorTiempo = {
    '30': {
        kpis: { total: 184, promedio: 4.90, tasa: '99.1%', registros: 184, comp: '+5.2% vs mes anterior' },
        tendencias: { labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'], data: [40, 55, 38, 51], titulo: 'Volumen Semanal' },
        tabla: [
            { id: 101, nombre: 'Juliana Sterling', dept: 'Ingeniería', fecha: 'Oct 24, 2023', score: 4.92, status: 'Aprobado', colorStatus: 'bg-success-subtle text-success' },
            { id: 102, nombre: 'Marcus Aurelius', dept: 'Operaciones', fecha: 'Oct 22, 2023', score: 3.80, status: 'Pendiente', colorStatus: 'bg-warning-subtle text-warning' }
        ]
    },
    'trimestre': {
        kpis: { total: 842, promedio: 4.75, tasa: '97.5%', registros: 842, comp: '+8.1% vs trimestre anterior' },
        tendencias: { labels: ['AGO', 'SEP', 'OCT'], data: [280, 310, 252], titulo: 'Volumen Mensual' },
        tabla: [
            { id: 103, nombre: 'Lydia Bennet', dept: 'RRHH', fecha: 'Sep 15, 2023', score: 4.15, status: 'Aprobado', colorStatus: 'bg-success-subtle text-success' },
            { id: 104, nombre: 'Darcy Williams', dept: 'Ingeniería', fecha: 'Ago 28, 2023', score: 4.88, status: 'Aprobado', colorStatus: 'bg-success-subtle text-success' }
        ]
    },
    'anual': {
        kpis: { total: 2842, promedio: 4.85, tasa: '98.2%', registros: 2842, comp: '+12.4% vs año anterior' },
        tendencias: { labels: ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT'], data: [180, 250, 210, 480, 320, 550, 400, 380, 420, 450], titulo: 'Volumen Anual' },
        tabla: [
            { id: 105, nombre: 'Jane Doe', dept: 'Operaciones', fecha: 'May 10, 2023', score: 4.50, status: 'Aprobado', colorStatus: 'bg-success-subtle text-success' }
        ]
    }
};

// --- FUNCIÓN PRINCIPAL DE CAMBIO ---
async function cambiarTemporalidad(tipo) {
    document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
    if(tipo === '30') document.getElementById('btn-30').classList.add('active');
    if(tipo === 'trimestre') document.getElementById('btn-trimestre').classList.add('active');
    if(tipo === 'anual') document.getElementById('btn-anual').classList.add('active');

    const data = DatosPorTiempo[tipo];

    renderKpis(data.kpis);
    document.getElementById('titulo-grafica').textContent = data.tendencias.titulo;
    document.getElementById('mostrando-count').textContent = data.tabla.length;
    
    renderTabla(data.tabla);

    if (chartTendencias) chartTendencias.destroy();
    chartTendencias = inicializarGraficaTendencias(data.tendencias);

    const depts = { departamentos: ['Ingeniería', 'Marketing', 'RRHH', 'Operaciones'], puntuaciones: [4.9, 4.7, 4.2, 4.5] };
    if (chartDept) chartDept.destroy();
    chartDept = inicializarGraficaDepartamentos(depts);
}

// --- INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", () => {
    cambiarTemporalidad('anual'); 
});

// --- FUNCIONES DE RENDER ---
function renderKpis(data) {
    document.getElementById('kpi-total').textContent = data.total.toLocaleString();
    document.getElementById('kpi-promedio').textContent = data.promedio.toFixed(2);
    document.getElementById('kpi-tasa').textContent = data.tasa;
    document.getElementById('total-registros').textContent = data.registros.toLocaleString();
    document.getElementById('kpi-comparativa').innerHTML = `<i class="bi bi-arrow-up-short fw-bold"></i> ${data.comp}`;
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
                <button class="btn btn-sm btn-light border text-primary fw-medium" onclick="verDetalleRegistro(${row.id})">
                    <i class="bi bi-eye me-1"></i> Ver
                </button>
            </td>
        </tr>
    `).join('');
}

// --- FUNCIÓN DEL "OJITO" (DETALLE INDIVIDUAL) ---
function verDetalleRegistro(id) {
    // Buscamos el registro en todos nuestros datos simulados
    let registro = null;
    Object.values(DatosPorTiempo).forEach(periodo => {
        const encontrado = periodo.tabla.find(r => r.id === id);
        if (encontrado) registro = encontrado;
    });

    if (!registro) return;

    // Simulación de desglose de KPIs para el modal
    const mensajeDetalle = `
        DETALLE DE EVALUACIÓN - ISA CORPORATIVO
        ---------------------------------------
        Colaborador: ${registro.nombre}
        Departamento: ${registro.dept}
        Puntuación Final: ${registro.score} / 5.0
        
        DESGLOSE DE CRITERIOS:
        - Competencias Técnicas: 4.8
        - Habilidades Blandas: 5.0
        - Productividad: ${registro.score > 4.5 ? 'Excepcional' : 'Estándar'}
        
        COMENTARIOS DEL EVALUADOR:
        "El desempeño mostrado en el periodo refleja un compromiso sólido con los objetivos de la empresa."
    `;

    alert(mensajeDetalle);
}

function inicializarGraficaTendencias(data) {
    const ctx = document.getElementById('chart-tendencias').getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Volumen',
                data: data.data,
                backgroundColor: ISA_COLORS.lightBlue,
                borderColor: ISA_COLORS.primary,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function inicializarGraficaDepartamentos(data) {
    const ctx = document.getElementById('chart-departamentos').getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.departamentos,
            datasets: [{
                data: data.puntuaciones,
                backgroundColor: ISA_COLORS.primary,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 5.0 } }
        }
    });
}