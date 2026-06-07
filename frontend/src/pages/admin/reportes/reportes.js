const ISA_COLORS = {
    primary: '#0d6efd',
    lightBlue: '#eef4ff',
    warning: '#ffc107',
    success: '#198754'
};

let chartTendencias = null;
let chartDept = null;

const ReportesAdminService = {
    async getEvaluaciones() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch {
            return [];
        }
    }
};

async function cambiarTemporalidad(tipo) {
    document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
    if(tipo === '30') document.getElementById('btn-30').classList.add('active');
    if(tipo === 'trimestre') document.getElementById('btn-trimestre').classList.add('active');
    if(tipo === 'anual') document.getElementById('btn-anual').classList.add('active');

    const evaluaciones = await ReportesAdminService.getEvaluaciones();
    const data = procesarDatos(evaluaciones, tipo);

    renderKpis(data.kpis);
    document.getElementById('titulo-grafica').textContent = data.tendencias.titulo;
    document.getElementById('mostrando-count').textContent = data.tabla.length;

    renderTabla(data.tabla);

    if (chartTendencias) chartTendencias.destroy();
    chartTendencias = inicializarGraficaTendencias(data.tendencias);

    const deptsData = agruparPorDepto(evaluaciones);
    if (chartDept) chartDept.destroy();
    chartDept = inicializarGraficaDepartamentos(deptsData);
}

function procesarDatos(evaluaciones, tipo) {
    const total = evaluaciones.length;
    const califs = evaluaciones.filter(e => e.calificacion_global != null).map(e => parseFloat(e.calificacion_global));
    const promedio = califs.length > 0 ? califs.reduce((a, b) => a + b, 0) / califs.length : 0;
    const aprobados = evaluaciones.filter(e => e.estado === 'APPROVED' || e.estado === 'CLOSED').length;
    const tasa = total > 0 ? (aprobados / total * 100).toFixed(1) + '%' : '0%';

    const labels = evaluaciones.slice(0, 10).map(e => {
        const d = e.fecha_creacion ? new Date(e.fecha_creacion) : new Date();
        return d.toLocaleDateString('es', { day: 'numeric', month: 'short' });
    });
    const valores = evaluaciones.slice(0, 10).map(e => e.calificacion_global ? parseFloat(e.calificacion_global) : 0);

    const tabla = evaluaciones.slice(0, 10).map(e => ({
        id: e.id,
        nombre: e.evaluado_nombre || e.evaluado || 'Sin nombre',
        dept: e.departamento_nombre || '—',
        fecha: e.fecha_actualizacion || e.fecha_creacion || '',
        score: e.calificacion_global ? parseFloat(e.calificacion_global) : 0,
        status: e.estado || 'PENDIENTE',
        colorStatus: e.estado === 'APPROVED' ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning'
    }));

    return {
        kpis: { total, promedio: promedio.toFixed(2), tasa, registros: total, comp: `vs periodo anterior` },
        tendencias: { labels: labels.reverse(), data: valores.reverse(), titulo: 'Evaluaciones recientes' },
        tabla
    };
}

function agruparPorDepto(evaluaciones) {
    const deptMap = {};
    evaluaciones.forEach(e => {
        const dept = e.departamento_nombre || 'Sin depto';
        if (!deptMap[dept]) deptMap[dept] = [];
        if (e.calificacion_global != null) deptMap[dept].push(parseFloat(e.calificacion_global));
    });
    return {
        departamentos: Object.keys(deptMap),
        puntuaciones: Object.values(deptMap).map(arr => arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : 0)
    };
}

document.addEventListener("DOMContentLoaded", () => {
    cambiarTemporalidad('anual');
});

function renderKpis(data) {
    document.getElementById('kpi-total').textContent = data.total.toLocaleString();
    document.getElementById('kpi-promedio').textContent = data.promedio;
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
            <td class="text-secondary">${row.fecha ? new Date(row.fecha).toLocaleDateString() : ''}</td>
            <td class="fw-bold fs-6">${row.score.toFixed(2)}</td>
            <td><span class="badge ${row.colorStatus} rounded-pill px-3">${row.status}</span></td>
            <td class="d-flex gap-1">
                <button class="btn btn-sm btn-light border text-primary fw-medium" onclick="verDetalleRegistro('${row.id}')">
                    <i class="bi bi-eye me-1"></i> Ver
                </button>
                <button class="btn btn-sm btn-success text-white fw-medium" onclick="generarPDF('${row.id}')">
                    <i class="bi bi-file-pdf me-1"></i> PDF
                </button>
            </td>
        </tr>
    `).join('');
}

async function generarPDF(id) {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Generando...';

    const token = localStorage.getItem('access_token') || '';
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    };

    try {
        const res = await fetch('http://localhost:8003/api/v1/generate', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                evaluacion_id: id,
                profile_name: 'default',
                institution_id: 'isa'
            })
        });

        if (!res.ok) throw new Error('Error al iniciar generación');

        const data = await res.json();
        const jobId = data.job_id;

        let statusData = { status: 'QUEUED' };
        const maxAttempts = 30;
        for (let i = 0; i < maxAttempts; i++) {
            await new Promise(r => setTimeout(r, 2000));
            const statusRes = await fetch(`http://localhost:8003/api/v1/status/${jobId}`, { headers });
            if (statusRes.ok) {
                statusData = await statusRes.json();
                if (statusData.status === 'SUCCESS' || statusData.status === 'FAILED') break;
            }
        }

        if (statusData.status === 'SUCCESS' && statusData.download_url) {
            window.open(statusData.download_url, '_blank');
        } else {
            alert('PDF generado, pero no se pudo descargar automáticamente.');
        }
    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-file-pdf me-1"></i> PDF';
    }
}

function verDetalleRegistro(id) {
    alert(`Detalle de evaluación ${id}`);
}

function inicializarGraficaTendencias(data) {
    const ctx = document.getElementById('chart-tendencias').getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Calificación',
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
            scales: { y: { beginAtZero: true, max: 5 } }
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
