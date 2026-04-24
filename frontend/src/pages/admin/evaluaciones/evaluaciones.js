let criteriaCount = 0;

// --- SIMULACIÓN DE BACKEND ---
const EvalService = {
    async publish(data) {
        console.log("Objeto final enviado a ISA Corporativo:", data);
        return { success: true };
    }
};

// --- LÓGICA DE INTERFAZ ---
function addCriterion(type) {
    criteriaCount++;
    const container = document.getElementById('criteria-container');
    const div = document.createElement('div');
    const uniqueId = Date.now(); // ID para identificar este bloque de opciones
    div.className = 'criteria-block shadow-sm question-item';
    
    let contentHtml = '';

    if (type === 'ESCALA LINEAL') {
        contentHtml = `
            <div class="mt-4 px-5">
                <input type="range" class="form-range" min="0" max="100">
                <div class="d-flex justify-content-between small text-muted">
                    <span>LIMITADO</span>
                    <span>VISIONARIO</span>
                </div>
            </div>`;
    } else if (type === 'OPCIÓN MÚLTIPLE') {
        // Plantilla con contenedor de opciones dinámicas
        contentHtml = `
            <div class="mt-3 px-5">
                <div id="options-container-${uniqueId}" class="d-flex flex-wrap gap-3 mb-2">
                    <div class="input-group input-group-sm" style="width: 200px;">
                        <span class="input-group-text bg-white border-end-0"><i class="bi bi-circle small"></i></span>
                        <input type="text" class="form-control border-start-0 ps-0 option-text" placeholder="Opción 1">
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-link text-primary p-0 text-decoration-none" 
                        onclick="addOptionField(${uniqueId})">
                    <i class="bi bi-plus-circle-fill"></i> Añadir otra opción
                </button>
            </div>`;
    } else {
        contentHtml = `
            <div class="mt-3 px-5">
                <textarea class="form-control bg-white" rows="2" placeholder="El usuario escribirá su respuesta aquí..." disabled></textarea>
            </div>`;
    }

    div.innerHTML = `
        <span class="badge bg-white text-primary border type-badge">${type}</span>
        <div class="row align-items-center">
            <div class="col-auto">
                <div class="rounded-circle bg-white border d-flex justify-content-center align-items-center" style="width:30px; height:30px; font-size: 0.8rem;">
                    ${criteriaCount < 10 ? '0'+criteriaCount : criteriaCount}
                </div>
            </div>
            <div class="col">
                <input type="text" class="form-control border-0 bg-transparent fw-bold question-input" 
                       data-type="${type}" data-id="${uniqueId}"
                       placeholder="Nombre del criterio o pregunta...">
            </div>
        </div>
        ${contentHtml}
    `;
    
    container.appendChild(div);
    document.getElementById('items-count').textContent = `${criteriaCount} ELEMENTOS AÑADIDOS`;
}

// Función para añadir campos de opción dinámicamente
function addOptionField(id) {
    const container = document.getElementById(`options-container-${id}`);
    const newOption = document.createElement('div');
    newOption.className = 'input-group input-group-sm animate__animated animate__fadeIn';
    newOption.style.width = '200px';
    newOption.innerHTML = `
        <span class="input-group-text bg-white border-end-0"><i class="bi bi-circle small"></i></span>
        <input type="text" class="form-control border-start-0 ps-0 option-text" placeholder="Nueva opción">
        <button class="btn btn-outline-danger border-0" onclick="this.parentElement.remove()"><i class="bi bi-x"></i></button>
    `;
    container.appendChild(newOption);
}

// Evento para publicar (Recoge preguntas + opciones)
document.getElementById('btn-publish').addEventListener('click', async () => {
    const evaluationData = {
        title: document.getElementById('eval-title').value,
        description: document.getElementById('eval-desc').value,
        audience: document.getElementById('eval-audience').value,
        criteria: []
    };
    
    const allQuestions = document.querySelectorAll('.question-input');

    allQuestions.forEach((input) => {
        const type = input.getAttribute('data-type');
        const qId = input.getAttribute('data-id');
        let options = [];

        // Si es múltiple, buscamos sus opciones específicas
        if (type === 'OPCIÓN MÚLTIPLE') {
            const optionInputs = document.querySelectorAll(`#options-container-${qId} .option-text`);
            optionInputs.forEach(opt => options.push(opt.value));
        }

        evaluationData.criteria.push({
            pregunta: input.value,
            tipo: type,
            opciones: options // Aquí se guardan las múltiples opciones
        });
    });

    if(!evaluationData.title || evaluationData.criteria.length === 0) {
        alert("Completa el título y añade al menos una pregunta.");
        return;
    }

    const res = await EvalService.publish(evaluationData);
    if(res.success) {
        alert("¡Publicada! Se guardaron " + evaluationData.criteria.length + " preguntas con sus opciones.");
        console.log("Datos enviados:", evaluationData);
    }
});

let grillaSupervision = null;

function abrirSupervision() {
    const modal = new bootstrap.Modal(document.getElementById('modalSupervision'));
    modal.show();
    
    setTimeout(() => {
        if (!grillaSupervision) {
            grillaSupervision = new GrillaSupervisor('grilla-supervision-container', {
                periodo: '2025-Q1'
            });
        }
    }, 100);
}

function filtrarUsuarios() {
    console.log('Filtrando usuarios...');
}