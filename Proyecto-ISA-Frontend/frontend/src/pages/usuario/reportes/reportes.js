const ReportesUserService = {
    async getMisEvaluaciones() {
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

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const evaluaciones = await ReportesUserService.getMisEvaluaciones();

        const metricas = procesarMetricas(evaluaciones);
        const competencias = procesarCompetencias(evaluaciones);
        const documentos = procesarDocumentos(evaluaciones);

        renderGraficaLinea(metricas);
        renderGraficaRadar(competencias);
        renderTablaDocumentos(documentos);
    } catch (error) {
        console.error("Error al cargar datos:", error);
    }
});

function procesarMetricas(evaluaciones) {
    const ordenadas = [...evaluaciones].sort((a, b) => {
        return new Date(a.fecha_creacion || 0) - new Date(b.fecha_creacion || 0);
    });
    return {
        etiquetas: ordenadas.slice(0, 12).map(e => {
            const d = e.fecha_creacion ? new Date(e.fecha_creacion) : new Date();
            return d.toLocaleDateString('es', { month: 'short', year: '2-digit' });
        }),
        valores: ordenadas.slice(0, 12).map(e => e.calificacion_global ? parseFloat(e.calificacion_global) : 0)
    };
}

function procesarCompetencias(evaluaciones) {
    return {
        categorias: ["Técnica", "Cultura", "Liderazgo", "Soft Skills", "Puntualidad"],
        valores: [85, 80, 75, 90, 95]
    };
}

function procesarDocumentos(evaluaciones) {
    return evaluaciones.slice(0, 10).map(e => ({
        id: e.id,
        periodo: e.periodo_nombre || '—',
        tipo: 'Evaluación',
        score: e.calificacion_global ? parseFloat(e.calificacion_global) : 0,
        fecha: e.fecha_actualizacion ? new Date(e.fecha_actualizacion).toLocaleDateString() : (e.fecha_creacion ? new Date(e.fecha_creacion).toLocaleDateString() : '—'),
        status: e.estado || ''
    }));
}

function renderGraficaLinea(data) {
    const ctx = document.getElementById('chart-crecimiento-personal').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.etiquetas,
            datasets: [{
                label: 'Mi Puntuación',
                data: data.valores,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 5 } } }
    });
}

function renderGraficaRadar(data) {
    const ctx = document.getElementById('chart-competencias-radar').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.categorias,
            datasets: [{
                label: 'Nivel Actual (%)',
                data: data.valores,
                backgroundColor: 'rgba(25, 135, 84, 0.2)',
                borderColor: '#198754',
                pointBackgroundColor: '#198754'
            }]
        },
        options: { scales: { r: { suggestMin: 0, suggestMax: 100 } } }
    });
}

function renderTablaDocumentos(documentos) {
    const tbody = document.getElementById('tabla-reportes-usuario');
    tbody.innerHTML = documentos.map(doc => `
        <tr>
            <td class="fw-bold">${doc.periodo}</td>
            <td>${doc.tipo}</td>
            <td><span class="badge bg-primary-subtle text-primary">${doc.score.toFixed(2)} / 5.0</span></td>
            <td>${doc.fecha}</td>
            <td class="text-end">
                <button class="btn btn-sm btn-light border" onclick="descargarPDF('${doc.id}')">Descargar PDF</button>
            </td>
        </tr>
    `).join('');
}

async function descargarPDF(id) {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>';

    try {
        const res = await fetch('http://localhost:8003/api/v1/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || '')
            },
            body: JSON.stringify({
                evaluacion_id: id,
                profile_name: 'default',
                institution_id: 'isa'
            })
        });

        if (!res.ok) throw new Error('Error al generar PDF');

        const data = await res.json();
        const jobId = data.job_id;

        let statusData = { status: 'QUEUED' };
        const maxAttempts = 30;
        for (let i = 0; i < maxAttempts; i++) {
            await new Promise(r => setTimeout(r, 2000));
            const statusRes = await fetch(`http://localhost:8003/api/v1/status/${jobId}`, {
                headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('access_token') || '') }
            });
            if (statusRes.ok) {
                statusData = await statusRes.json();
                if (statusData.status === 'SUCCESS' || statusData.status === 'FAILED') break;
            }
        }

        if (statusData.status === 'SUCCESS' && statusData.download_url) {
            window.open(statusData.download_url, '_blank');
        } else {
            alert('El PDF está listo pero no se pudo descargar automáticamente. Revisa más tarde.');
        }
    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Descargar PDF';
    }
}
