/**
 * SERVICIO DE EVALUACIONES (Capa de Datos)
 */
const EvaluacionesUserService = {
    async getPendientes() {
        return [
            { id: 201, titulo: "Autoevaluación Mensual - Octubre", limite: "Oct 25, 2023", categoria: "Cultura" },
            { id: 202, titulo: "Feedback 360: Equipo TI", limite: "Oct 28, 2023", categoria: "Liderazgo" }
        ];
    },

    async getHistorial() {
        return [
            { id: 50, titulo: "Evaluación Técnica Q3", fecha: "Sep 15, 2023", evaluador: "Sistema / IA", score: 4.8 },
            { id: 48, titulo: "Soft Skills", fecha: "Ago 02, 2023", evaluador: "Admin Corp", score: 5.0 }
        ];
    }
};

let grillaISA = null;

function abrirGrillaEvaluacion() {
    const modal = new bootstrap.Modal(document.getElementById('modalGrilla'));
    modal.show();
    
    setTimeout(() => {
        if (!grillaISA) {
            grillaISA = new GrillaISA('grilla-evaluacion-container', {
                evaluacionId: '2025-Q1',
                periodo: 'Q1 2025',
                readOnly: false,
                onSave: (data) => {
                    console.log('Evaluación guardada:', data);
                    document.getElementById('stat-ultimo-cambio').textContent = new Date().toLocaleTimeString();
                }
            });
        }
    }, 100);
}

/**
 * CONTROLADOR
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [pendientes, historial] = await Promise.all([
            EvaluacionesUserService.getPendientes(),
            EvaluacionesUserService.getHistorial()
        ]);

        renderPendientes(pendientes);
        renderHistorial(historial);
    } catch (error) {
        console.error("Falla en backend al obtener evaluaciones:", error);
    }
});

function renderPendientes(lista) {
    const contenedor = document.getElementById('contenedor-pendientes');
    if (lista.length === 0) {
        contenedor.innerHTML = '<p class="text-muted small ps-2">No tienes tareas pendientes hoy. ✨</p>';
        return;
    }

    contenedor.innerHTML = lista.map(p => `
        <div class="col-md-6">
            <div class="card border p-3 shadow-sm h-100">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <span class="badge bg-warning-subtle text-warning mb-2">${p.categoria}</span>
                        <h6 class="fw-bold mb-1">${p.titulo}</h6>
                        <p class="text-muted smaller mb-0">Vence: ${p.limite}</p>
                    </div>
                    <button class="btn btn-primary btn-sm px-3" onclick="comenzarEncuesta(${p.id})">Responder</button>
                </div>
            </div>
        </div>
    `).join('');
}

function renderHistorial(lista) {
    const tabla = document.getElementById('tabla-historial');
    tabla.innerHTML = lista.map(h => `
        <tr>
            <td class="fw-bold text-dark-blue">${h.titulo}</td>
            <td>${h.fecha}</td>
            <td>${h.evaluador}</td>
            <td><span class="fw-bold text-primary">${h.score.toFixed(1)}</span></td>
            <td>
                <button class="btn btn-sm btn-light border" onclick="verCertificado(${h.id})">📑 Ver Reporte</button>
            </td>
        </tr>
    `).join('');
}

// Funciones para acciones (Backend Ready)
function comenzarEncuesta(id) {
    alert("Redirigiendo al cuestionario ID: " + id);
    // window.location.href = `../responder/responder.html?id=${id}`;
}

function verCertificado(id) {
    alert("Generando PDF para la evaluación: " + id);
}