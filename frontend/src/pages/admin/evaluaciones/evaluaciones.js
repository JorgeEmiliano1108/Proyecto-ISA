let criteriaCount = 0;
const evaluationData = {
    title: "",
    description: "",
    audience: "",
    criteria: []
};

// --- SIMULACIÓN DE BACKEND (SERVICIOS) ---
const EvalService = {
    async publish(data) {
        console.log("Enviando al backend:", data);
        // En el futuro: return fetch('api/evaluations', { method: 'POST', body: JSON.stringify(data) });
        return { success: true, id: Date.now() };
    }
};

// --- LÓGICA DE INTERFAZ ---
function addCriterion(type) {
    criteriaCount++;
    const container = document.getElementById('criteria-container');
    const div = document.createElement('div');
    div.className = 'criteria-block shadow-sm';
    
    // Plantilla dinámica basada en el tipo (Totalmente en español)
    div.innerHTML = `
        <span class="badge bg-white text-primary border type-badge">${type}</span>
        <div class="row align-items-center">
            <div class="col-auto">
                <div class="rounded-circle bg-white border d-flex justify-content-center align-items-center" style="width:30px; height:30px; font-size: 0.8rem;">
                    ${criteriaCount < 10 ? '0'+criteriaCount : criteriaCount}
                </div>
            </div>
            <div class="col">
                <input type="text" class="form-control border-0 bg-transparent fw-bold" placeholder="Nombre del criterio o pregunta...">
            </div>
        </div>
        ${type === 'ESCALA LINEAL' ? `
            <div class="mt-4 px-5">
                <input type="range" class="form-range" min="0" max="100">
                <div class="d-flex justify-content-between small text-muted">
                    <span>LIMITADO</span>
                    <span>VISIONARIO</span>
                </div>
            </div>
        ` : type === 'OPCIÓN MÚLTIPLE' ? `
            <div class="mt-3 px-5 d-flex gap-4">
                <div class="form-check"><input class="form-check-input" type="radio" disabled> <label class="small">Líder Emergente</label></div>
                <div class="form-check"><input class="form-check-input" type="radio" disabled> <label class="small">Experto Consolidado</label></div>
            </div>
        ` : `
            <div class="mt-3 px-5">
                <textarea class="form-control bg-white" rows="2" placeholder="El usuario escribirá su respuesta aquí..." disabled></textarea>
            </div>
        `}
    `;
    
    container.appendChild(div);
    // Traducción del contador
    document.getElementById('items-count').textContent = `${criteriaCount} ${criteriaCount === 1 ? 'ELEMENTO AÑADIDO' : 'ELEMENTOS AÑADIDOS'}`;
}

// Evento para publicar
document.getElementById('btn-publish').addEventListener('click', async () => {
    evaluationData.title = document.getElementById('eval-title').value;
    evaluationData.description = document.getElementById('eval-desc').value;
    evaluationData.audience = document.getElementById('eval-audience').value;
    
    if(!evaluationData.title) {
        alert("Por favor, ponle un título a la evaluación");
        return;
    }

    const res = await EvalService.publish(evaluationData);
    if(res.success) {
        alert("¡Evaluación publicada con éxito!");
    }
});