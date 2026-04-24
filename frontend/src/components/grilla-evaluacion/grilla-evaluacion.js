/**
 * GRILLA DINÁMICA ISA - Sistema de Evaluación de Desempeño
 * Powered by Handsontable
 */

class GrillaISA {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.hot = null;
        this.options = {
            evaluacionId: options.evaluacionId || null,
            periodo: options.periodo || '2025-Q1',
            readOnly: options.readOnly || false,
            onSave: options.onSave || ((data) => console.log('Guardando:', data)),
            onCellChange: options.onCellChange || null
        };
        
        this.registroCambios = [];
        this.debounceTimer = null;
        
        this.init();
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Contenedor #${this.containerId} no encontrado`);
            return;
        }

        const data = this.generarDatosModelo();
        
        this.hot = new Handsontable(container, {
            data: data,
            rowHeaders: true,
            colHeaders: [
                '#', 'Nombre', 'Puesto', 
                'Liderazgo', 'Comunicación', 'Proactividad', 
                'Colaboración', 'Adaptabilidad', 'Orient. Resultados',
                'Promedio', 'Evaluación Global', 'Estado'
            ],
            columns: [
                { data: 0, type: 'numeric', readOnly: true, width: 40 },
                { data: 1, type: 'text', editor: 'text' },
                { data: 2, type: 'text', editor: 'text' },
                { data: 3, type: 'numeric', editor: 'numeric', renderer: this.calificacionRenderer },
                { data: 4, type: 'numeric', editor: 'numeric', renderer: this.calificacionRenderer },
                { data: 5, type: 'numeric', editor: 'numeric', renderer: this.calificacionRenderer },
                { data: 6, type: 'numeric', editor: 'numeric', renderer: this.calificacionRenderer },
                { data: 7, type: 'numeric', editor: 'numeric', renderer: this.calificacionRenderer },
                { data: 8, type: 'numeric', editor: 'numeric', renderer: this.calificacionRenderer },
                { data: 9, type: 'numeric', readOnly: true },
                { data: 10, type: 'numeric', readOnly: true },
                { data: 11, type: 'text', readOnly: true }
            ],
            licenseKey: 'non-commercial-and-evaluation',
            readOnly: false,
            height: 'auto',
            minRows: 5,
            contextMenu: true,
            manualRowMove: true,
            search: true,
            filters: true,
            dropdownMenu: true,
            afterChange: (changes, source) => this.handleCellChange(changes, source),
            cells: (row, col) => this.estilosCelda(row, col),
            sanitizer: (html) => html
        });
    }

    generarDatosModelo() {
        return [
            [1, 'Juan Pérez', 'Arquitecto Sr.', 4, 5, 3, 4, 5, 4, '', '', 'Borrador'],
            [2, 'María García', 'Líder de Equipo', 5, 4, 5, 4, 4, 5, '', '', 'Borrador'],
            [3, 'Carlos López', 'Desarrollador', 3, 4, 4, 5, 3, 4, '', '', 'Borrador'],
            [4, 'Ana Martínez', 'Diseñadora UI', 4, 5, 5, 4, 5, 5, '', '', 'Borrador'],
            [5, 'Pedro Sánchez', 'QA Engineer', 4, 3, 4, 4, 4, 3, '', '', 'Borrador']
        ];
    }

    calificacionRenderer(hotInstance, td, row, col, prop, value, cellProperties) {
        td.textContent = value || '';
        
        const colores = {
            1: '#ffcccc',
            2: '#ffe6cc',
            3: '#ffffcc',
            4: '#ccffcc',
            5: '#ccffff'
        };
        
        if (value >= 1 && value <= 5) {
            td.style.backgroundColor = colores[value] || '#fff';
            td.style.fontWeight = 'bold';
            td.style.textAlign = 'center';
        }
        
        return td;
    }

    estilosCelda(row, col) {
        if (col >= 3 && col <= 8) {
            return {
                className: 'calificacion-cell text-center'
            };
        }
        if (col === 9 || col === 10) {
            return {
                className: 'promedio-cell bg-light fw-bold text-center'
            };
        }
        if (col === 11) {
            return {
                className: 'estado-cell'
            };
        }
        return {};
    }

    handleCellChange(changes, source) {
        if (source !== 'edit' && source !== 'paste') return;
        
        changes.forEach(([row, prop, oldValue, newValue]) => {
            if (oldValue !== newValue) {
                this.registrarCambio(row, prop, oldValue, newValue);
            }
        });
        
        this.calcularPromedios();
        this.autoGuardar();
    }

    registrarCambio(row, col, oldVal, newVal) {
        const columnas = ['', 'nombre', 'puesto', 'liderazgo', 'comunicacion', 'proactividad', 'colaboracion', 'adaptabilidad', 'orientacion'];
        const nombreCol = columnas[col] || `col_${col}`;
        
        this.registroCambios.push({
            fila: row,
            columna: nombreCol,
            valorAnterior: oldVal,
            valorNuevo: newVal,
            timestamp: new Date().toISOString()
        });
    }

    calcularPromedios() {
        const hot = this.hot;
        const data = hot.getData();
        
        let sumaTotal = 0;
        let countTotal = 0;
        
        data.forEach((fila, idx) => {
            const calificaciones = [
                parseFloat(fila[3]) || 0,
                parseFloat(fila[4]) || 0,
                parseFloat(fila[5]) || 0,
                parseFloat(fila[6]) || 0,
                parseFloat(fila[7]) || 0,
                parseFloat(fila[8]) || 0
            ].filter(v => v > 0);
            
            const promedio = calificaciones.length > 0 
                ? (calificaciones.reduce((a, b) => a + b, 0) / calificaciones.length).toFixed(2)
                : '';
            
            const evalGlobal = promedio ? (promedio * 0.8).toFixed(2) : '';
            
            hot.setDataAtCell(idx, 9, promedio);
            hot.setDataAtCell(idx, 10, evalGlobal);
            
            const estado = promedio ? 'En Proceso' : 'Borrador';
            hot.setDataAtCell(idx, 11, estado);
            
            // Acumular para promedio general
            calificaciones.forEach(c => {
                sumaTotal += c;
                countTotal++;
            });
        });
        
        // Actualizar stats en el DOM
        const promedioGeneral = countTotal > 0 ? (sumaTotal / countTotal).toFixed(2) : '0.00';
        const statPromedio = document.getElementById('stat-promedio-general');
        const statEmpleados = document.getElementById('stat-empleados');
        
        if (statPromedio) statPromedio.textContent = promedioGeneral;
        if (statEmpleados) statEmpleados.textContent = data.length;
        
        // Actualizar estado
        const estadoEval = document.getElementById('estado-evaluacion');
        if (estadoEval) {
            if (promedioGeneral > '0') {
                estadoEval.className = 'estado-evaluacion en-proceso';
                estadoEval.innerHTML = '<span class="spinner-border spinner-border-sm" style="width: 10px; height: 10px;"></span> En Proceso';
            } else {
                estadoEval.className = 'estado-evaluacion borrador';
                estadoEval.textContent = 'Borrador';
            }
        }
    }

    autoGuardar() {
        clearTimeout(this.debounceTimer);
        
        this.debounceTimer = setTimeout(() => {
            this.guardar();
            
            // Actualizar tiempo de última modificación
            const statTiempo = document.getElementById('stat-ultimo-cambio');
            if (statTiempo) {
                const ahora = new Date();
                statTiempo.textContent = ahora.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
            }
            
            this.mostrarNotificacion('✅ Cambios guardados automáticamente');
        }, 2000);
    }

    guardar() {
        const data = this.hot.getData();
        const evaluacion = {
            id: this.options.evaluacionId,
            periodo: this.options.periodo,
            empleados: data.map((fila, idx) => ({
                id: fila[0],
                nombre: fila[1],
                puesto: fila[2],
                competencias: {
                    liderazgo: fila[3],
                    comunicacion: fila[4],
                    proactividad: fila[5],
                    colaboracion: fila[6],
                    adaptabilidad: fila[7],
                    orientacion_resultados: fila[8]
                },
                promedio: fila[9],
                evaluacion_global: fila[10],
                estado: fila[11]
            })),
            cambios: this.registroCambios,
            fechaModificacion: new Date().toISOString()
        };
        
        localStorage.setItem(`isa_evaluacion_${this.options.periodo}`, JSON.stringify(evaluacion));
        
        if (this.options.onSave) {
            this.options.onSave(evaluacion);
        }
        
        console.log('📦 Evaluación guardada:', evaluacion);
    }

    cargar() {
        const key = `isa_evaluacion_${this.options.periodo}`;
        const data = localStorage.getItem(key);
        
        if (data) {
            const evaluacion = JSON.parse(data);
            const rows = evaluacion.empleados.map(e => [
                e.id, e.nombre, e.puesto,
                e.competencias.liderazgo,
                e.competencias.comunicacion,
                e.competencias.proactividad,
                e.competencias.colaboracion,
                e.competencias.adaptabilidad,
                e.competencias.orientacion_resultados,
                e.promedio,
                e.evaluacion_global,
                e.estado
            ]);
            
            this.hot.loadData(rows);
            this.calcularPromedios();
            console.log('📂 Evaluación cargada:', evaluacion.periodo);
        }
    }

agregarFila() {
        const rowIndex = this.hot.countRows();
        this.hot.alter('insert_row', rowIndex);
        
        // Agregar valores por defecto
        const nuevoId = rowIndex + 1;
        const nuevaFila = [nuevoId, 'Nuevo Empleado', 'Puesto', '', '', '', '', '', '', '', 'Borrador'];
        
        for (let col = 0; col < nuevaFila.length; col++) {
            this.hot.setDataAtCell(rowIndex, col, nuevaFila[col]);
        }
        
        this.mostrarNotificacion('➕ Fila agregada');
    }

    mostrarNotificacion(mensaje) {
        const notif = document.createElement('div');
        notif.className = 'position-fixed bottom-0 end-0 m-3 badge bg-success text-white px-3 py-2';
        notif.style.zIndex = '9999';
        notif.textContent = mensaje;
        document.body.appendChild(notif);
        
        setTimeout(() => notif.remove(), 3000);
    }

    getData() {
        return this.hot ? this.hot.getData() : [];
    }

    destroy() {
        if (this.hot) {
            this.hot.destroy();
            this.hot = null;
        }
    }
}

/**
 * ADMIN - Supervisión de Todas las Evaluaciones
 */
class GrillaSupervisor {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.hot = null;
        this.options = options;
        
        this.init();
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const data = this.generarDatosSupervision();
        
        this.hot = new Handsontable(container, {
            data: data,
            rowHeaders: true,
            colHeaders: [
                '#', 'Usuario', 'Estado', 
                'Liderazgo', 'Comunicación', 'Proactividad', 
                'Colaboración', 'Adaptabilidad', 'Orient. Resultados',
                'Promedio', 'Evaluación Global', 'Última Modificación', 'Acciones'
            ],
            columns: [
                { data: 0, type: 'numeric', readOnly: true, width: 40 },
                { data: 1, type: 'text', readOnly: true },
                { data: 2, type: 'text', readOnly: true, renderer: this.estadoRenderer },
                { data: 3, type: 'numeric', readOnly: true },
                { data: 4, type: 'numeric', readOnly: true },
                { data: 5, type: 'numeric', readOnly: true },
                { data: 6, type: 'numeric', readOnly: true },
                { data: 7, type: 'numeric', readOnly: true },
                { data: 8, type: 'numeric', readOnly: true },
                { data: 9, type: 'numeric', readOnly: true },
                { data: 10, type: 'numeric', readOnly: true },
                { data: 11, type: 'text', readOnly: true },
                { data: 12, type: 'text', renderer: this.accionesRenderer }
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
        return [
            [1, 'Juan Pérez', 'En Proceso', 4, 5, 3, 4, 5, 4, 4.17, 3.34, '2025-01-15 10:30', '<button class="btn btn-sm btn-primary">Ver</button>'],
            [2, 'María García', 'Completado', 5, 4, 5, 4, 4, 5, 4.50, 3.60, '2025-01-14 16:45', '<button class="btn btn-sm btn-success">Ver</button>'],
            [3, 'Carlos López', 'Borrador', 3, 4, 4, 5, 3, 4, 3.83, 3.06, '2025-01-10 09:15', '<button class="btn btn-sm btn-warning">Ver</button>'],
            [4, 'Ana Martínez', 'En Proceso', 4, 5, 5, 4, 5, 5, 4.67, 3.74, '2025-01-15 11:20', '<button class="btn btn-sm btn-primary">Ver</button>'],
            [5, 'Pedro Sánchez', 'Borrador', 4, 3, 4, 4, 4, 3, 3.67, 2.94, '2025-01-12 14:00', '<button class="btn btn-sm btn-warning">Ver</button>']
        ];
    }

    estadoRenderer(hotInstance, td, row, col, prop, value, cellProperties) {
        td.textContent = value || '';
        
        const colores = {
            'Borrador': '#6c757d',
            'En Proceso': '#ffc107',
            'Completado': '#198754',
            'Aprobado': '#0d6efd'
        };
        
        td.className = 'badge';
        td.style.backgroundColor = colores[value] || '#6c757d';
        td.style.color = '#fff';
        td.style.padding = '4px 8px';
        
        return td;
    }

    accionesRenderer(hotInstance, td, row, col, prop, value, cellProperties) {
        td.innerHTML = value || '';
        return td;
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