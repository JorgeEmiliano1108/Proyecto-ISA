/**
 * SERVICIO DE BONOS (Backend Interface)
 */
const BonosUserService = {
    async getInfoBonoActual() {
        // En Backend: SELECT * FROM bonos_usuario WHERE id_usuario = ? AND activo = 1
        return {
            nombre: "Bono de Desempeño Trimestral (Q4)",
            descripcion: "Basado en el cumplimiento de objetivos técnicos y de cultura.",
            progreso: 75,
            montoProyectado: "$12,450.00",
            fechaInicio: "01 Oct 2023",
            fechaCierre: "31 Dic 2023",
            estado: "En Proceso"
        };
    },

    async getMetasVinculadas() {
        return [
            { titulo: "Disponibilidad de Servidores", meta: "99.9%", actual: "99.5%", icono: "🖥️" },
            { titulo: "Certificación Cloud", meta: "1", actual: "1", icono: "📜" },
            { titulo: "Feedback de Equipo", meta: "4.5/5", actual: "4.2/5", icono: "🤝" }
        ];
    },

    async getHistorialPagos() {
        return [
            { fecha: "Jul 15, 2023", concepto: "Bono Q2", monto: "$10,200.00", estado: "Pagado" },
            { fecha: "Abr 15, 2023", concepto: "Bono Q1", monto: "$9,800.00", estado: "Pagado" }
        ];
    }
};

/**
 * CONTROLADOR
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const [bono, metas, historial] = await Promise.all([
            BonosUserService.getInfoBonoActual(),
            BonosUserService.getMetasVinculadas(),
            BonosUserService.getHistorialPagos()
        ]);

        renderBonoPrincipal(bono);
        renderMetas(metas);
        renderHistorial(historial);
    } catch (error) {
        console.error("Error al obtener datos de bonos del servidor:", error);
    }
});

function renderBonoPrincipal(data) {
    document.getElementById('bono-activo-info').innerHTML = `
        <h4 class="fw-bold text-primary mb-1">${data.nombre}</h4>
        <p class="text-muted small mb-3">${data.descripcion}</p>
    `;
    const barra = document.getElementById('barra-progreso-bono');
    barra.style.width = `${data.progreso}%`;
    barra.textContent = `${data.progreso}%`;
    
    document.getElementById('fecha-inicio').textContent = data.fechaInicio;
    document.getElementById('fecha-cierre').textContent = data.fechaCierre;
    document.getElementById('monto-proyectado').textContent = data.montoProyectado;
}

function renderMetas(metas) {
    const contenedor = document.getElementById('lista-metas');
    contenedor.innerHTML = metas.map(m => `
        <div class="d-flex align-items-center mb-3 p-2 border-bottom">
            <div class="fs-4 me-3">${m.icono}</div>
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
    tabla.innerHTML = pagos.map(p => `
        <tr>
            <td class="small">
                <strong>${p.concepto}</strong><br>
                <span class="smaller text-muted">${p.fecha}</span>
            </td>
            <td class="text-end fw-bold text-success">${p.monto}</td>
            <td class="text-end"><span class="badge bg-light text-dark border smaller">✓</span></td>
        </tr>
    `).join('');
}