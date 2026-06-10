const EvaluacionesUserService = {
    async getEvaluaciones() {
        try {
            const res = await apiFetch('/evaluations/');
            if (!res.ok) return [];
            const data = await res.json();
            return data.results || data;
        } catch {
            return [];
        }
    },

    async getEvaluacion(id) {
        try {
            const res = await apiFetch(`/evaluations/${id}/`);
            if (!res.ok) return null;
            return await res.json();
        } catch {
            return null;
        }
    },

    async enviarEvaluacion(id) {
        const res = await apiFetch(`/evaluations/${id}/submit/`, { method: 'POST' });
        return res.ok ? await res.json() : null;
    },

    getPendientes(evaluaciones) {
        return evaluaciones.filter(
            e => ['DRAFT', 'SUBMITTED', 'PENDING_APPROVAL'].includes(e.estado)
        );
    },

    getHistorial(evaluaciones) {
        return evaluaciones.filter(
            e => ['APPROVED', 'CLOSED', 'REJECTED'].includes(e.estado)
        );
    }
};

let grillaISA = null;
let evaluacionActualId = null;

function abrirGrillaEvaluacion(evalId) {
    evaluacionActualId = evalId;
    const modal = new bootstrap.Modal(document.getElementById('modalGrilla'));
    modal.show();

    const btnEnviar = document.getElementById('btn-enviar-evaluacion');
    btnEnviar.classList.add('d-none');

    const estadoEnvio = document.getElementById('estado-envio');
    estadoEnvio.classList.add('d-none');

    setTimeout(async () => {
        const container = document.getElementById('grilla-evaluacion-container');
        container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary mb-3"></div><p class="text-muted">Cargando formulario de evaluación...</p></div>';

        if (grillaISA) {
            grillaISA.destroy();
            grillaISA = null;
        }

        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        let datosCargados = null;

        if (evalId) {
            const apiData = await EvaluacionesUserService.getEvaluacion(evalId);
            if (apiData) {
                datosCargados = mapearAPIDatosGrilla(apiData, userData);
                if (apiData.estado === 'DRAFT') {
                    btnEnviar.classList.remove('d-none');
                } else {
                    estadoEnvio.classList.remove('d-none');
                    estadoEnvio.textContent = `Estado: ${apiData.estado}`;
                    if (apiData.estado === 'SUBMITTED') {
                        estadoEnvio.className = 'badge bg-warning-subtle text-warning px-3 py-2';
                    } else if (apiData.estado === 'PENDING_APPROVAL') {
                        estadoEnvio.className = 'badge bg-info-subtle text-info px-3 py-2';
                    } else {
                        estadoEnvio.className = 'badge bg-secondary-subtle text-secondary px-3 py-2';
                    }
                }
            }
        }

        grillaISA = new GrillaISA('grilla-evaluacion-container', {
            evaluacionId: evalId || 'eval-' + Date.now(),
            periodo: datosCargados?.periodo || '2025',
            fileId: null,
            readOnly: datosCargados && !(datosCargados.estado === 'DRAFT' || !datosCargados.estado),
            onSave: (data) => {
                guardarEvaluacionEnBD(data, grillaISA.options.evaluacionId);
                const ahora = new Date();
                const timeStr = ahora.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
                const notif = document.createElement('div');
                notif.className = 'position-fixed bottom-0 end-0 m-3 badge bg-success text-white px-3 py-2 shadow';
                notif.style.zIndex = '9999';
                notif.innerHTML = `<i class="bi bi-check-circle me-1"></i>Guardado ${timeStr}`;
                document.body.appendChild(notif);
                setTimeout(() => notif.remove(), 3000);
            }
        });

        if (datosCargados) {
            grillaISA.populateData(datosCargados);
        }
    }, 100);
}

function mapearAPIDatosGrilla(apiData, userData) {
    const competencias = {};
    if (apiData.competencias) {
        apiData.competencias.forEach((c, idx) => {
            competencias[idx + 1] = c.calificacion || 0;
        });
    }

    return {
        colaborador: apiData.evaluado_nombre || userData.nombre || '',
        puesto_colaborador: apiData.evaluado_puesto || '',
        evaluador: apiData.evaluador_nombre || '',
        puesto_evaluador: '',
        jefe_inmediato: '',
        puesto_jefe: '',
        fecha_ingreso: '',
        fecha_evaluacion: apiData.fecha_creacion ? apiData.fecha_creacion.split('T')[0] : '',
        fecha_revision: '',
        periodo: apiData.periodo_nombre || '2025',
        resultados_2025: apiData.logros_previos || '',
        compromisos_2026: '',
        competencias: competencias,
        evaluacion_global: apiData.calificacion_global != null ? String(apiData.calificacion_global) : '',
        comentarios_evaluador: apiData.comentarios_evaluador || '',
        comentarios_colaborador: apiData.comentarios_evaluado || '',
        firma_colaborador: '',
        fecha_entrega: '',
        firma_evaluador: '',
        firma_jefe: '',
        estado: apiData.estado
    };
}

async function guardarEvaluacionEnBD(data, evaluacionId) {
    try {
        const competencias = [];
        for (let i = 1; i <= 6; i++) {
            if (data.competencias && data.competencias[i]) {
                competencias.push({
                    competencia: i,
                    calificacion: data.competencias[i]
                });
            }
        }

        const payload = {
            logros_previos: data.resultados_2025 || '',
            comentarios_evaluador: data.comentarios_evaluador || '',
            comentarios_evaluado: data.comentarios_colaborador || '',
            calificacion_global: parseFloat(data.evaluacion_global) || null,
            competencias: competencias.length > 0 ? competencias : undefined
        };

        const id = evaluacionId;
        if (!id) {
            console.error('No hay ID de evaluación para guardar');
            return;
        }

        const res = await apiFetch(`/evaluations/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            console.error('Error guardando evaluación:', await res.text());
        }
    } catch (e) {
        console.error('Error guardando evaluación en BD:', e);
    }
}

async function enviarEvaluacion() {
    if (!evaluacionActualId) return;

    const confirmacion = confirm('¿Estás seguro de enviar esta evaluación? Una vez enviada no podrás editarla hasta que sea revisada.');
    if (!confirmacion) return;

    const btn = document.getElementById('btn-enviar-evaluacion');
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';

    try {
        const result = await EvaluacionesUserService.enviarEvaluacion(evaluacionActualId);
        if (result) {
            alert('Evaluación enviada correctamente.');
            location.reload();
        } else {
            alert('Error al enviar la evaluación. Intenta de nuevo.');
        }
    } catch (e) {
        alert('Error de conexión al enviar la evaluación.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const evaluaciones = await EvaluacionesUserService.getEvaluaciones();
        const pendientes = EvaluacionesUserService.getPendientes(evaluaciones);
        const historial = EvaluacionesUserService.getHistorial(evaluaciones);

        renderPendientes(pendientes);
        renderHistorial(historial);
    } catch (error) {
        console.error("Falla en backend al obtener evaluaciones:", error);
    }

    document.getElementById('btn-enviar-evaluacion')?.addEventListener('click', enviarEvaluacion);
});

function renderPendientes(lista) {
    const contenedor = document.getElementById('contenedor-pendientes');
    if (lista.length === 0) {
        contenedor.innerHTML = '<p class="text-muted small ps-2">No tienes evaluaciones pendientes.</p>';
        return;
    }

    contenedor.innerHTML = lista.map(p => {
        const estadoLabel = {
            DRAFT: 'Borrador',
            SUBMITTED: 'En revisión',
            PENDING_APPROVAL: 'Pendiente de aprobación'
        }[p.estado] || p.estado;

        const estadoBadge = {
            DRAFT: 'bg-warning-subtle text-warning',
            SUBMITTED: 'bg-info-subtle text-info',
            PENDING_APPROVAL: 'bg-primary-subtle text-primary'
        }[p.estado] || 'bg-secondary-subtle text-secondary';

        const puedeEditar = p.estado === 'DRAFT';

        return `
        <div class="col-md-6">
            <div class="card border p-3 shadow-sm h-100">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <span class="badge bg-warning-subtle text-warning mb-2">${p.periodo_nombre || 'Sin periodo'}</span>
                        <span class="badge ${estadoBadge} mb-2 ms-1">${estadoLabel}</span>
                        <h6 class="fw-bold mb-1">${p.evaluador_nombre || 'Evaluación'}</h6>
                        <p class="text-muted smaller mb-0">${p.evaluado_puesto || ''}</p>
                    </div>
                    <button class="btn ${puedeEditar ? 'btn-primary' : 'btn-outline-secondary'} btn-sm px-3" onclick="abrirGrillaEvaluacion('${p.id}')">
                        ${puedeEditar ? 'Responder' : 'Ver'}
                    </button>
                </div>
            </div>
        </div>
    `}).join('');
}

function renderHistorial(lista) {
    const tabla = document.getElementById('tabla-historial');
    if (lista.length === 0) {
        tabla.innerHTML = `<tr><td colspan="5" class="text-center text-muted small py-3">Sin evaluaciones completadas</td></tr>`;
        return;
    }
    tabla.innerHTML = lista.map(h => `
        <tr>
            <td class="fw-bold text-dark-blue">${h.periodo_nombre || 'Evaluación'}</td>
            <td>${h.fecha_creacion ? new Date(h.fecha_creacion).toLocaleDateString('es-MX') : '--'}</td>
            <td>${h.evaluador_nombre || '--'}</td>
            <td><span class="fw-bold text-primary">${h.calificacion_global ? Number(h.calificacion_global).toFixed(1) : '--'}</span></td>
            <td>
                <button class="btn btn-sm btn-light border" onclick="verCertificado('${h.id}')"> Ver Reporte</button>
            </td>
        </tr>
    `).join('');
}

function comenzarEncuesta(id) {
    abrirGrillaEvaluacion();
}

function verCertificado(id) {
    alert("Reporte para evaluación: " + id);
}
