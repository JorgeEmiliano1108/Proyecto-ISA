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

const EXCEL_FILE_ID = '';

function abrirGrillaEvaluacion() {
    const modal = new bootstrap.Modal(document.getElementById('modalGrilla'));
    modal.show();

    const estadoConexion = document.getElementById('estado-conexion');

    setTimeout(() => {
        if (!grillaISA) {
            grillaISA = new GrillaISA('grilla-evaluacion-container', {
                evaluacionId: 'eval-discrecional-2025',
                periodo: '2025',
                fileId: EXCEL_FILE_ID || null,
                onSave: (data) => {
                    const ahora = new Date();
                    const timeStr = ahora.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
                    const notif = document.createElement('div');
                    notif.className = 'position-fixed bottom-0 end-0 m-3 badge bg-success text-white px-3 py-2 shadow';
                    notif.style.zIndex = '9999';
                    notif.innerHTML = `<i class="bi bi-check-circle me-1"></i>Guardado ${timeStr}`;
                    document.body.appendChild(notif);
                    setTimeout(() => notif.remove(), 3000);
                },
                onLoad: (data) => {
                    actualizarEstadoConexion(true);
                }
            });
        }
        verificarSesion();
    }, 100);
}

async function verificarSesion() {
    const estadoConexion = document.getElementById('estado-conexion');
    try {
        const loggedIn = await MSGraphService.isLoggedIn();
        if (loggedIn) {
            actualizarEstadoConexion(true);
            if (EXCEL_FILE_ID) {
                grillaISA.cargar();
            }
        } else {
            estadoConexion.className = 'estado-evaluacion';
            estadoConexion.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i>Conectando...';
            await MSGraphService.login();
            actualizarEstadoConexion(true);
            if (EXCEL_FILE_ID) {
                grillaISA.cargar();
            }
        }
    } catch (e) {
        console.error('Error de autenticación:', e);
        estadoConexion.className = 'estado-evaluacion';
        estadoConexion.innerHTML = '<i class="bi bi-exclamation-triangle me-1"></i>No conectado';
        estadoConexion.style.background = 'rgba(239, 68, 68, 0.3)';
    }
}

function actualizarEstadoConexion(conectado) {
    const estadoConexion = document.getElementById('estado-conexion');
    if (!estadoConexion) return;
    if (conectado) {
        estadoConexion.className = 'estado-evaluacion completado';
        estadoConexion.innerHTML = '<i class="bi bi-check-circle me-1"></i>OneDrive Conectado';
        estadoConexion.style.background = 'rgba(16, 185, 129, 0.3)';
    } else {
        estadoConexion.className = 'estado-evaluacion';
        estadoConexion.innerHTML = '<i class="bi bi-x-circle me-1"></i>Desconectado';
        estadoConexion.style.background = 'rgba(239, 68, 68, 0.3)';
    }
}

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
                <button class="btn btn-sm btn-light border" onclick="verCertificado(${h.id})"> Ver Reporte</button>
            </td>
        </tr>
    `).join('');
}

function comenzarEncuesta(id) {
    alert("Redirigiendo al cuestionario ID: " + id);
}

function verCertificado(id) {
    alert("Generando PDF para la evaluación: " + id);
}
