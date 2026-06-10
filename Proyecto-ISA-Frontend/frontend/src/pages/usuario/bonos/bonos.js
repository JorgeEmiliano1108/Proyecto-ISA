/**
 * SERVICIO DE BONOS USUARIO - Capa de servicio para comunicación con API Django.
 * Reemplaza los mocks hardcodeados por llamadas reales a la API Django.
 */
import { BonosService } from '../../services/bonos.js';

/**
 * CONTROLADOR
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [bono, metas, historial] = await Promise.all([
            BonosService.getInfoBonoActual(),
            BonosService.getMetasVinculadas(),
            BonosService.getHistorialPagos()
        ]);

        renderBonoPrincipal(bono);
        renderMetas(metas);
        renderHistorial(historial);
    } catch (error) {
        console.error("Error al obtener datos de bonos del servidor:", error);
        // Fallback a estado vacío
        renderBonoPrincipal({});
        renderMetas([]);
        renderHistorial([]);
    }
});

function renderBonoPrincipal(data) {
    const infoContainer = document.getElementById('bono-activo-info');
    if (infoContainer) {
        infoContainer.innerHTML = `
            <h4 class="fw-bold text-primary mb-1">${data.nombre || 'Sin bono asignado'}</h4>
            <p class="text-muted small mb-3">${data.descripcion || 'Sin descripción disponible'}</p>
        `;
    }
    
    const barra = document.getElementById('barra-progreso-bono');
    if (barra) {
        barra.style.width = `${data.progreso || 0}%`;
        barra.textContent = `${data.progreso || 0}%`;
    }
    
    document.getElementById('fecha-inicio').textContent = data.fechaInicio || '--';
    document.getElementById('fecha-cierre').textContent = data.fechaCierre || '--';
    document.getElementById('monto-proyectado').textContent = data.montoProyectado || '$0.00';
}

function renderMetas(metas) {
    const contenedor = document.getElementById('lista-metas');
    if (!contenedor) return;
    
    if (!metas || metas.length === 0) {
        contenedor.innerHTML = '<p class="text-muted text-center py-3">No hay metas vinculadas</p>';
        return;
    }
    
    contenedor.innerHTML = metas.map(m => `
        <div class="d-flex align-items-center mb-3 p-2 border-bottom">
            <div class="fs-4 me-3">${m.icono || '🎯'}</div>
            <div class="flex-grow-1">
                <h6 class="mb-0 small fw-bold">${m.titulo}</h6>
                <div class="d-flex justify-content-between">
                    <span class="smaller text-muted">Meta: ${m.meta}</span>
                    <span class="smaller fw-bold text-primary">Actual: ${m.actual}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderHistorial(pagos) {
    const tabla = document.getElementById('tabla-historial-bonos');
    if (!tabla) return;
    
    if (!pagos || pagos.length === 0) {
        tabla.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-3">Sin historial de pagos</td></tr>';
        return;
    }
    
    tabla.innerHTML = pagos.map(p => `
        <tr>
            <td class="small">
                <strong>${p.concepto || 'Bono'}</strong><br>
                <span class="smaller text-muted">${p.fecha || ''}</span>
            </td>
            <td class="text-end fw-bold text-success">${p.monto || '$0.00'}</td>
            <td class="text-end"><span class="badge bg-light text-dark border smaller">✓</span></td>
        </tr>
    `).join('');
}