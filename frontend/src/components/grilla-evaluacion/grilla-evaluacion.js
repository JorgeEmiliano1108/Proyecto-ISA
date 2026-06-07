class GrillaISA {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            evaluacionId: options.evaluacionId || 'eval-' + Date.now(),
            periodo: options.periodo || '2025',
            fileId: options.fileId || null,
            readOnly: options.readOnly || false,
            onSave: options.onSave || ((data) => console.log('Guardando:', data)),
            onLoad: options.onLoad || null
        };
        this.datos = this.getInitialData();
        this.init();
    }

    getInitialData() {
        return {
            colaborador: '',
            puesto_colaborador: '',
            evaluador: '',
            puesto_evaluador: '',
            jefe_inmediato: '',
            puesto_jefe: '',
            fecha_ingreso: '',
            fecha_evaluacion: '',
            fecha_revision: '',
            periodo: this.options.periodo,
            resultados_2025: '',
            compromisos_2026: '',
            competencias: {
                1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0
            },
            evaluacion_global: '',
            comentarios_evaluador: '',
            comentarios_colaborador: '',
            firma_colaborador: '',
            fecha_entrega: '',
            firma_evaluador: '',
            firma_jefe: ''
        };
    }

    getCompetencias() {
        return [
            { id: 1, nombre: '1. Orientación al cliente', descripcion: 'Disponibilidad y Flexibilidad' },
            { id: 2, nombre: '2. Enfoque a resultados', descripcion: 'Identificar las prioridades' },
            { id: 3, nombre: '3. Confiabilidad', descripcion: 'Capacidad para adaptarse y Disponibilidad' },
            { id: 4, nombre: '4. Trabajo en equipo', descripcion: 'Apoyo a compañeros y Flexibilidad para tomar nuevas tareas' },
            { id: 5, nombre: '5. Innovación y desarrollo', descripcion: 'Propuestas de mejoras' },
            { id: 6, nombre: '6. Liderazgo', descripcion: 'Capacidad de llevar adelante proyectos e iniciativas y motivar a su equipo' }
        ];
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Contenedor #${this.containerId} no encontrado`);
            return;
        }
        container.innerHTML = this.renderForm();
        this.bindEvents();
    }

    renderForm() {
        const competencias = this.getCompetencias();
        const c = this.datos;

        const rowsCompetencias = competencias.map(comp => {
            const radios = [1, 2, 3, 4, 5].map(nivel => `
                <td class="radio-cell nivel-${nivel}">
                    <input type="radio" name="competencia_${comp.id}" value="${nivel}"
                        ${c.competencias[comp.id] === nivel ? 'checked' : ''}
                        ${this.options.readOnly ? 'disabled' : ''}>
                </td>
            `).join('');
            return `
                <tr>
                    <td class="comp-nombre">
                        <span class="fw-semibold">${comp.nombre}</span>
                        <small class="text-muted d-block">${comp.descripcion}</small>
                    </td>
                    ${radios}
                </tr>
            `;
        }).join('');

        const readOnlyAttr = this.options.readOnly ? 'disabled' : '';
        const readOnlyClass = this.options.readOnly ? 'disabled-input' : '';

        return `
            <div class="grilla-form">
                <div class="grilla-toolbar">
                    <div class="d-flex gap-2">
                        <button class="btn btn-primary" id="btn-guardar-grilla" ${readOnlyAttr}>
                            <i class="bi bi-save"></i> Guardar
                        </button>
                        <button class="btn btn-outline-secondary" id="btn-cargar-grilla" ${readOnlyAttr}>
                            <i class="bi bi-cloud-download"></i> Cargar desde Excel
                        </button>
                    </div>
                    <div class="grilla-leyenda">
                        <span><i class="bi bi-palette me-1"></i>Escala:</span>
                        <div class="grilla-leyenda-item"><span class="color-dot c1">1</span><span class="small">Bajo</span></div>
                        <div class="grilla-leyenda-item"><span class="color-dot c2">2</span><span class="small">Regular</span></div>
                        <div class="grilla-leyenda-item"><span class="color-dot c3">3</span><span class="small">Bueno</span></div>
                        <div class="grilla-leyenda-item"><span class="color-dot c4">4</span><span class="small">Muy Bueno</span></div>
                        <div class="grilla-leyenda-item"><span class="color-dot c5">5</span><span class="small">Excelente</span></div>
                    </div>
                </div>

                <div class="form-section">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Colaborador</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-colaborador" value="${c.colaborador}" ${readOnlyAttr}>
                            <input type="text" class="form-control form-control-sm mt-1 ${readOnlyClass}" id="campo-puesto-colaborador" placeholder="Puesto" value="${c.puesto_colaborador}" ${readOnlyAttr}>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Evaluador</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-evaluador" value="${c.evaluador}" ${readOnlyAttr}>
                            <input type="text" class="form-control form-control-sm mt-1 ${readOnlyClass}" id="campo-puesto-evaluador" placeholder="Puesto" value="${c.puesto_evaluador}" ${readOnlyAttr}>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Jefe Inmediato del Evaluador</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-jefe" value="${c.jefe_inmediato}" ${readOnlyAttr}>
                            <input type="text" class="form-control form-control-sm mt-1 ${readOnlyClass}" id="campo-puesto-jefe" placeholder="Puesto" value="${c.puesto_jefe}" ${readOnlyAttr}>
                        </div>
                    </div>

                    <div class="row g-3 mt-2">
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Fecha de Ingreso</label>
                            <input type="date" class="form-control form-control-sm ${readOnlyClass}" id="campo-fecha-ingreso" value="${c.fecha_ingreso}" ${readOnlyAttr}>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Fecha de Evaluación</label>
                            <input type="date" class="form-control form-control-sm ${readOnlyClass}" id="campo-fecha-evaluacion" value="${c.fecha_evaluacion}" ${readOnlyAttr}>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Fecha de Revisión</label>
                            <input type="date" class="form-control form-control-sm ${readOnlyClass}" id="campo-fecha-revision" value="${c.fecha_revision}" ${readOnlyAttr}>
                        </div>
                    </div>

                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Período de Evaluación</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-periodo" value="${c.periodo}" ${readOnlyAttr}>
                        </div>
                    </div>
                </div>

                <div class="form-section bg-light">
                    <p class="small text-muted mb-0 fst-italic px-3 py-2">
                        Se revisarán los resultados alcanzados durante el año en curso, el desarrollo de las competencias claves y las áreas de mejora, así como los compromisos para el siguiente año. Al evaluar las competencias tomar en cuenta que el nivel menor es 1 y el mayor 5. También la Evaluación Global no tiene que ser necesariamente un promedio de las evaluaciones de las competencias. Una vez revisada con tu jefe inmediato, la evaluación deberá ser entregada al colaborador y firmada por él durante la sesión de retroalimentación.
                    </p>
                </div>

                <div class="form-section">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label fw-bold text-primary small text-uppercase">Resultados 2025 <span class="text-muted fw-normal">(Logros y Áreas de Mejora)</span></label>
                            <textarea class="form-control ${readOnlyClass}" id="campo-resultados-2025" rows="4" ${readOnlyAttr}>${c.resultados_2025}</textarea>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-bold text-success small text-uppercase">Compromisos/Objetivos 2026</label>
                            <textarea class="form-control ${readOnlyClass}" id="campo-compromisos-2026" rows="4" ${readOnlyAttr}>${c.compromisos_2026}</textarea>
                        </div>
                    </div>
                </div>

                <div class="alert alert-warning alert-nota d-flex align-items-center gap-2 py-2 px-3 small mb-0" role="alert">
                    <i class="bi bi-exclamation-triangle"></i>
                    EN TODOS LOS CASOS LA EVALUACION DEBE SER REVISADA POR EL JEFE INMEDIATO DEL EVALUADOR ANTES DE SER ENTREGADA Y REVISADA CON EL COLABORADOR
                </div>

                <div class="form-section">
                    <h6 class="fw-bold text-center mb-3 text-uppercase" style="color: var(--grilla-primary);">
                        <i class="bi bi-grid me-2"></i>Evaluación de Competencias
                    </h6>
                    <div class="competencias-table-wrapper">
                        <table class="table table-bordered competencias-table">
                            <thead>
                                <tr>
                                    <th style="width: 40%;">Competencias</th>
                                    <th class="nivel-header">1</th>
                                    <th class="nivel-header">2</th>
                                    <th class="nivel-header">3</th>
                                    <th class="nivel-header">4</th>
                                    <th class="nivel-header">5</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsCompetencias}
                            </tbody>
                        </table>
                    </div>
                    <div class="mt-3 text-center small text-muted">
                        <i class="bi bi-info-circle me-1"></i>Nivel 1 (menor) a 5 (mayor)
                    </div>
                </div>

                <div class="form-section bg-light">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <label class="form-label fw-bold text-uppercase mb-0" style="color: var(--grilla-primary);">
                                <i class="bi bi-star me-1"></i>Evaluación Global
                            </label>
                            <p class="text-muted small mb-0">(no es necesario que sea un promedio de las de arriba)</p>
                        </div>
                        <div class="col-md-4">
                            <div class="input-group">
                                <input type="number" class="form-control form-control-lg text-center fw-bold eval-global-input ${readOnlyClass}"
                                    id="campo-eval-global" min="1" max="5" step="0.1"
                                    value="${c.evaluacion_global}" ${readOnlyAttr}>
                                <span class="input-group-text">/ 5</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label fw-semibold text-muted small text-uppercase">
                                <i class="bi bi-chat-quote me-1"></i>Comentarios del Evaluador
                            </label>
                            <textarea class="form-control ${readOnlyClass}" id="campo-comentarios-evaluador" rows="3" ${readOnlyAttr}>${c.comentarios_evaluador}</textarea>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold text-muted small text-uppercase">
                                <i class="bi bi-chat-quote me-1"></i>Comentarios del Colaborador
                            </label>
                            <textarea class="form-control ${readOnlyClass}" id="campo-comentarios-colaborador" rows="3" ${readOnlyAttr}>${c.comentarios_colaborador}</textarea>
                        </div>
                    </div>
                </div>

                <div class="form-section border-top">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Nombre y Firma del Colaborador</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-firma-colaborador" value="${c.firma_colaborador}" ${readOnlyAttr}>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Fecha de Revisión y Entrega</label>
                            <input type="date" class="form-control form-control-sm ${readOnlyClass}" id="campo-fecha-entrega" value="${c.fecha_entrega}" ${readOnlyAttr}>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Nombre y Firma del Evaluador</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-firma-evaluador" value="${c.firma_evaluador}" ${readOnlyAttr}>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-4">
                            <label class="form-label fw-semibold text-muted small text-uppercase">Nombre y Firma del Jefe Inmediato</label>
                            <input type="text" class="form-control form-control-sm ${readOnlyClass}" id="campo-firma-jefe" value="${c.firma_jefe}" ${readOnlyAttr}>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.getElementById('btn-guardar-grilla')?.addEventListener('click', () => this.guardar());
        document.getElementById('btn-cargar-grilla')?.addEventListener('click', () => this.cargar());

        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', () => this.onCompetenciaChange());
        });

        document.querySelectorAll('.form-control, .form-select').forEach(input => {
            input.addEventListener('change', () => this.onFieldChange());
            input.addEventListener('input', () => this.onFieldChange());
        });
    }

    collectData() {
        const getVal = (id) => {
            const el = document.getElementById(id);
            return el ? el.value : '';
        };

        const competencias = {};
        for (let i = 1; i <= 6; i++) {
            const selected = document.querySelector(`input[name="competencia_${i}"]:checked`);
            competencias[i] = selected ? parseInt(selected.value) : 0;
        }

        return {
            colaborador: getVal('campo-colaborador'),
            puesto_colaborador: getVal('campo-puesto-colaborador'),
            evaluador: getVal('campo-evaluador'),
            puesto_evaluador: getVal('campo-puesto-evaluador'),
            jefe_inmediato: getVal('campo-jefe'),
            puesto_jefe: getVal('campo-puesto-jefe'),
            fecha_ingreso: getVal('campo-fecha-ingreso'),
            fecha_evaluacion: getVal('campo-fecha-evaluacion'),
            fecha_revision: getVal('campo-fecha-revision'),
            periodo: getVal('campo-periodo'),
            resultados_2025: getVal('campo-resultados-2025'),
            compromisos_2026: getVal('campo-compromisos-2026'),
            competencias: competencias,
            evaluacion_global: getVal('campo-eval-global'),
            comentarios_evaluador: getVal('campo-comentarios-evaluador'),
            comentarios_colaborador: getVal('campo-comentarios-colaborador'),
            firma_colaborador: getVal('campo-firma-colaborador'),
            fecha_entrega: getVal('campo-fecha-entrega'),
            firma_evaluador: getVal('campo-firma-evaluador'),
            firma_jefe: getVal('campo-firma-jefe')
        };
    }

    populateData(data) {
        this.datos = data;
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = this.renderForm();
            this.bindEvents();
        }
    }

    onCompetenciaChange() {
        const data = this.collectData();
        this.datos = data;
    }

    onFieldChange() {
        const data = this.collectData();
        this.datos = data;
    }

    async guardar() {
        const data = this.collectData();
        const fileId = this.options.fileId;

        if (!fileId) {
            this.mostrarNotificacion('⚠️ Configura el File ID del Excel en OneDrive', 'warning');
            return;
        }

        const gridData = this.buildExcelData(data);

        try {
            await MSGraphService.updateExcelWorksheetRange(fileId, 'FORMATO', 'A1:Q51', gridData);
            this.mostrarNotificacion('✅ Evaluación guardada en Excel correctamente', 'success');
            if (this.options.onSave) this.options.onSave(data);
        } catch (e) {
            console.error('Error al guardar:', e);
            this.mostrarNotificacion('❌ Error al guardar: ' + e.message, 'danger');
        }
    }

    async cargar() {
        const fileId = this.options.fileId;

        if (!fileId) {
            this.mostrarNotificacion('⚠️ Configura el File ID del Excel en OneDrive', 'warning');
            return;
        }

        try {
            this.mostrarNotificacion('🔄 Cargando datos desde Excel...', 'info');
            const result = await MSGraphService.getExcelWorksheetRange(fileId, 'FORMATO', 'A1:Q51');
            const values = result.values;

            if (!values || values.length === 0) {
                this.mostrarNotificacion('⚠️ El Excel está vacío', 'warning');
                return;
            }

            const data = this.parseExcelData(values);
            this.populateData(data);
            this.mostrarNotificacion('✅ Datos cargados desde Excel', 'success');
            if (this.options.onLoad) this.options.onLoad(data);
        } catch (e) {
            console.error('Error al cargar:', e);
            if (e.message.includes('No autenticado')) {
                this.mostrarNotificacion('🔑 Necesitas iniciar sesión con Microsoft', 'warning');
            } else {
                this.mostrarNotificacion('❌ Error al cargar: ' + e.message, 'danger');
            }
        }
    }

    buildExcelData(data) {
        const grid = [];
        for (let r = 0; r < 51; r++) {
            grid[r] = [];
            for (let c = 0; c < 17; c++) {
                grid[r][c] = null;
            }
        }

        grid[4][0] = 'EVALUACIÓN DE DESEMPEÑO DISCRECIONAL';

        grid[7][0] = 'Colaborador';
        grid[7][1] = data.colaborador || '';
        grid[7][6] = 'Evaluador:';
        grid[7][7] = data.evaluador || '';
        grid[7][12] = 'Jefe Inmediato del Evaluador:';
        grid[7][13] = data.jefe_inmediato || '';

        grid[9][0] = 'Puesto:';
        grid[9][1] = data.puesto_colaborador || '';
        grid[9][6] = 'Puesto:';
        grid[9][7] = data.puesto_evaluador || '';
        grid[9][12] = 'Puesto:';
        grid[9][13] = data.puesto_jefe || '';

        grid[11][0] = 'Fecha de ingreso:';
        grid[11][1] = data.fecha_ingreso || '';
        grid[11][6] = 'Fecha de evaluación.';
        grid[11][7] = data.fecha_evaluacion || '';
        grid[11][12] = 'Fecha de revisión:';
        grid[11][13] = data.fecha_revision || '';

        grid[13][0] = 'Periodo de evaluación:';
        grid[13][1] = data.periodo || '';

        const resultadosLines = this.splitIntoLines(data.resultados_2025 || '', 6);
        for (let i = 0; i < resultadosLines.length && i < 6; i++) {
            grid[21 + i][0] = resultadosLines[i];
        }
        const compromisosLines = this.splitIntoLines(data.compromisos_2026 || '', 6);
        for (let i = 0; i < compromisosLines.length && i < 6; i++) {
            grid[21 + i][9] = compromisosLines[i];
        }

        grid[28][9] = 'Nivel (1 menor a 5 mayor)';

        grid[29][1] = 'Competencias';
        grid[29][9] = 1;
        grid[29][10] = 2;
        grid[29][11] = 3;
        grid[29][12] = 4;
        grid[29][13] = 5;

        const compNombres = [
            '1. Orientación al cliente (Disponibilidad y Flexibilidad)',
            '2. Enfoque a resultados (Identificar las prioridades)',
            '3. Confiabilidad (Capacidad para adaptarse y Disponibilidad)',
            '4. Trabajo en equipo (Apoyo a compañeros y Flexibilidad para tomar nuevas tareas)',
            '5. Innovación y desarrollo (Propuestas de mejoras)',
            '6. Liderazgo (Capacidad de llevar adelante proyectos e iniciativas y motivar a su equipo)'
        ];

        for (let i = 0; i < 6; i++) {
            const row = 30 + i;
            grid[row][1] = compNombres[i];
            const nivel = data.competencias[i + 1] || 0;
            if (nivel >= 1 && nivel <= 5) {
                grid[row][8 + nivel] = nivel;
            }
        }

        grid[36][4] = 'EVALUACION GLOBAL (no es necesario que sea un promedio de las de arriba)';
        const evalGlobal = parseFloat(data.evaluacion_global);
        if (!isNaN(evalGlobal) && evalGlobal >= 1 && evalGlobal <= 5) {
            grid[36][9] = evalGlobal;
        }

        grid[39][0] = 'Comentarios de la persona que hace la Evaluación (Evaluador):';
        const evalLines = this.splitIntoLines(data.comentarios_evaluador || '', 2);
        for (let i = 0; i < evalLines.length; i++) {
            grid[40 + i][0] = evalLines[i];
        }

        grid[42][0] = 'Comentarios de la persona Evaluada (Colaborador):';
        const colabLines = this.splitIntoLines(data.comentarios_colaborador || '', 2);
        for (let i = 0; i < colabLines.length; i++) {
            grid[43 + i][0] = colabLines[i];
        }

        grid[49][0] = 'Nombre y firma del Colaborador';
        grid[49][1] = data.firma_colaborador || '';
        grid[49][4] = 'Fecha de revisión y entrega al Colaborador';
        grid[49][5] = data.fecha_entrega || '';
        grid[49][9] = 'Nombre y Firma del Evaluador';
        grid[49][10] = data.firma_evaluador || '';
        grid[49][13] = 'Nombre y Firma del Jefe inmediato';
        grid[49][14] = data.firma_jefe || '';

        return grid;
    }

    parseExcelData(values) {
        const data = this.getInitialData();

        const getCell = (r, c) => {
            if (r < values.length && c < (values[r] || []).length) {
                const v = values[r][c];
                return v !== null && v !== undefined ? String(v).trim() : '';
            }
            return '';
        };

        data.colaborador = getCell(7, 1) || getCell(7, 2);
        data.evaluador = getCell(7, 7);
        data.jefe_inmediato = getCell(7, 13);
        data.puesto_colaborador = getCell(9, 1);
        data.puesto_evaluador = getCell(9, 7);
        data.puesto_jefe = getCell(9, 13);
        data.fecha_ingreso = getCell(11, 1);
        data.fecha_evaluacion = getCell(11, 7);
        data.fecha_revision = getCell(11, 13);
        data.periodo = getCell(13, 1);

        const resultadosParts = [];
        for (let r = 21; r <= 26; r++) {
            const v = getCell(r, 0);
            if (v) resultadosParts.push(v);
        }
        data.resultados_2025 = resultadosParts.join('\n');

        const compromisosParts = [];
        for (let r = 21; r <= 26; r++) {
            const v = getCell(r, 9);
            if (v) compromisosParts.push(v);
        }
        data.compromisos_2026 = compromisosParts.join('\n');

        for (let i = 0; i < 6; i++) {
            const row = 30 + i;
            let nivel = 0;
            for (let col = 9; col <= 13; col++) {
                const v = getCell(row, col);
                if (v) {
                    const parsed = parseInt(v);
                    if (parsed >= 1 && parsed <= 5) {
                        nivel = parsed;
                        break;
                    }
                }
            }
            data.competencias[i + 1] = nivel;
        }

        const evalGlobal = getCell(36, 9);
        data.evaluacion_global = evalGlobal;

        const evalComentarios = [];
        for (let r = 39; r <= 41; r++) {
            const v = getCell(r, 0);
            if (v && !v.includes('Comentarios de la persona')) evalComentarios.push(v);
        }
        data.comentarios_evaluador = evalComentarios.join('\n');

        const colabComentarios = [];
        for (let r = 43; r <= 45; r++) {
            const v = getCell(r, 0);
            if (v && !v.includes('Comentarios de la persona')) colabComentarios.push(v);
        }
        data.comentarios_colaborador = colabComentarios.join('\n');

        data.firma_colaborador = getCell(49, 1);
        data.fecha_entrega = getCell(49, 5);
        data.firma_evaluador = getCell(49, 10);
        data.firma_jefe = getCell(49, 14);

        return data;
    }

    splitIntoLines(text, maxLines) {
        const lines = text.split('\n');
        const result = [];
        for (const line of lines) {
            if (result.length >= maxLines) break;
            result.push(line);
        }
        return result;
    }

    mostrarNotificacion(mensaje, tipo = 'success') {
        const notif = document.createElement('div');
        const bgClass = tipo === 'success' ? 'bg-success' : tipo === 'warning' ? 'bg-warning text-dark' : tipo === 'danger' ? 'bg-danger' : 'bg-info text-dark';
        notif.className = `position-fixed bottom-0 end-0 m-3 badge ${bgClass} px-3 py-2 shadow`;
        notif.style.zIndex = '9999';
        notif.textContent = mensaje;
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), 4000);
    }

    destroy() {
        const container = document.getElementById(this.containerId);
        if (container) container.innerHTML = '';
    }
}

class GrillaSupervisor {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.hot = null;
        this.options = options;
        if (options.data) {
            this.initWithData(options.data);
        } else {
            this.init();
        }
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        this.renderHot(this.generarDatosSupervision());
    }

    initWithData(data) {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        this.renderHot(this.mapearDatosAPI(data));
    }

    mapearDatosAPI(evaluaciones) {
        return evaluaciones.map((ev, idx) => [
            idx + 1,
            ev.evaluado_nombre || ev.evaluado || '—',
            ev.estado || '—',
            ev.calificacion_global ? Number(ev.calificacion_global).toFixed(2) : '—',
            ev.fecha_actualizacion || ev.fecha_creacion || '—',
            ev.periodo_nombre || '—',
            ev.evaluador_nombre || '—'
        ]);
    }

    renderHot(data) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        this.hot = new Handsontable(container, {
            data: data,
            rowHeaders: true,
            colHeaders: [
                '#', 'Evaluado', 'Estado',
                'Calificación', 'Última Modificación', 'Período', 'Evaluador'
            ],
            columns: [
                { data: 0, type: 'numeric', readOnly: true, width: 40 },
                { data: 1, type: 'text', readOnly: true },
                { data: 2, type: 'text', readOnly: true, renderer: this.estadoRenderer },
                { data: 3, type: 'text', readOnly: true },
                { data: 4, type: 'text', readOnly: true },
                { data: 5, type: 'text', readOnly: true },
                { data: 6, type: 'text', readOnly: true }
            ],
            licenseKey: 'non-commercial-and-evaluation',
            readOnly: true,
            height: 'auto',
            contextMenu: true,
            search: true,
            filters: true,
            dropdownMenu: true
        });
    }

    generarDatosSupervision() {
        return [];
    }

    estadoRenderer(hotInstance, td, row, col, prop, value, cellProperties) {
        td.textContent = value || '';
        const colores = {
            'DRAFT': '#6c757d',
            'SUBMITTED': '#ffc107',
            'PENDING_APPROVAL': '#fd7e14',
            'APPROVED': '#198754',
            'CLOSED': '#0d6efd',
            'REJECTED': '#dc3545'
        };
        td.className = 'badge';
        td.style.backgroundColor = colores[value] || '#6c757d';
        td.style.color = '#fff';
        td.style.padding = '4px 8px';
        return td;
    }

    updateData(data) {
        if (this.hot) {
            this.hot.destroy();
        }
        this.initWithData(data);
    }

    destroy() {
        if (this.hot) {
            this.hot.destroy();
            this.hot = null;
        }
    }
}

window.GrillaISA = GrillaISA;
window.GrillaSupervisor = GrillaSupervisor;
