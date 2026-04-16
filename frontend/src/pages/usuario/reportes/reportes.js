/**
 * SERVICIO DE REPORTES (Backend Interface)
 */
const ReportesUserService = {
    async getMetricasHistoricas() {
        // En Backend: SELECT mes, score FROM resultados WHERE user_id = ? ORDER BY fecha ASC
        return {
            etiquetas: ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            valores: [4.2, 4.5, 4.3, 4.8, 4.7, 4.9]
        };
    },
    async getCompetencias() {
        return {
            categorias: ["Técnica", "Cultura", "Liderazgo", "Soft Skills", "Puntualidad"],
            valores: [95, 88, 70, 92, 100]
        };
    },
    async getDocumentos() {
        return [
            { id: 1, periodo: "Q2 2023", tipo: "Evaluación Trimestral", score: 4.8, fecha: "15/07/2023" },
            { id: 2, periodo: "Anual 2022", tipo: "Cierre de Ciclo", score: 4.5, fecha: "10/01/2023" },
            { id: 3, periodo: "Q4 2022", tipo: "Evaluación Trimestral", score: 4.2, fecha: "15/10/2022" }
        ];
    }
};

/**
 * CONTROLADOR
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [metricas, competencias, documentos] = await Promise.all([
            ReportesUserService.getMetricasHistoricas(),
            ReportesUserService.getCompetencias(),
            ReportesUserService.getDocumentos()
        ]);

        renderGraficaLinea(metricas);
        renderGraficaRadar(competencias);
        renderTablaDocumentos(documentos);
    } catch (error) {
        console.error("Error al conectar con la base de datos de reportes:", error);
    }
});

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
        options: { responsive: true, plugins: { legend: { display: false } } }
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
            <td><span class="badge bg-primary-subtle text-primary">${doc.score} / 5.0</span></td>
            <td>${doc.fecha}</td>
            <td class="text-end">
                <button class="btn btn-sm btn-light border" onclick="descargarPDF(${doc.id})">📥 PDF</button>
            </td>
        </tr>
    `).join('');
}

function descargarPDF(id) {
    alert("Iniciando descarga segura del reporte ID: " + id);
}