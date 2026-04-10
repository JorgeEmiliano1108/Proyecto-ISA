class ISAApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEventListeners();
    }

    checkAuth() {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            this.showPage('login');
        } else {
            this.showPage('dashboard');
        }
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                this.showPage(page);
            }

            if (e.target.id === 'logout-btn') {
                this.logout();
            }
        });
    }

    async showPage(page) {
        const mainContent = document.getElementById('main-content');
        this.showLoading(true);

        try {
            switch (page) {
                case 'login':
                    mainContent.innerHTML = this.renderLogin();
                    break;
                case 'dashboard':
                    mainContent.innerHTML = await this.loadDashboard();
                    break;
                case 'evaluations':
                    mainContent.innerHTML = await this.loadEvaluations();
                    break;
                case 'bonos':
                    mainContent.innerHTML = await this.loadBonos();
                    break;
                case 'usuarios':
                    mainContent.innerHTML = await this.loadUsuarios();
                    break;
                case 'reportes':
                    mainContent.innerHTML = await this.loadReportes();
                    break;
                case 'aprobaciones':
                    mainContent.innerHTML = await this.loadAprobaciones();
                    break;
                default:
                    mainContent.innerHTML = await this.loadDashboard();
            }

            this.updateActiveMenu(page);
        } catch (error) {
            this.showToast('Error al cargar la página', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateActiveMenu(page) {
        document.querySelectorAll('.main-nav a').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });
    }

    renderLogin() {
        return `
            <div class="login-container">
                <div class="login-box">
                    <div class="login-logo">
                        <h1>Sistema ISA</h1>
                        <p>Evaluación de Desempeño</p>
                    </div>
                    <p class="login-subtitle">Ingrese sus credenciales para continuar</p>
                    <form id="login-form" class="login-form">
                        <div class="login-input-group">
                            <label for="username">Usuario</label>
                            <input type="text" class="login-input" id="username" placeholder="Ingrese su usuario" required>
                        </div>
                        <div class="login-input-group">
                            <label for="password">Contraseña</label>
                            <input type="password" class="login-input" id="password" placeholder="Ingrese su contraseña" required>
                        </div>
                        <button type="submit" class="login-btn" id="login-btn">Iniciar Sesión</button>
                    </form>
                </div>
            </div>
        `;
    }

    async loadDashboard() {
        const data = await this.apiRequest('/dashboard/');
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Dashboard</h2>
                </div>
                <div class="dashboard-grid">
                    <div class="stat-card">
                        <div class="stat-value">${data.total_evaluations || 0}</div>
                        <div class="stat-label">Total Evaluaciones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.pending || 0}</div>
                        <div class="stat-label">Pendientes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.approved || 0}</div>
                        <div class="stat-label">Aprobadas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.rejected || 0}</div>
                        <div class="stat-label">Rechazadas</div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadEvaluations() {
        const data = await this.apiRequest('/evaluations/');
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Evaluaciones</h2>
                    <button class="btn btn-primary" onclick="app.showEvaluationForm()">Nueva Evaluación</button>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Empleado</th>
                                <th>Periodo</th>
                                <th>Estado</th>
                                <th>Fecha</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.map(evaluation => `
                                <tr>
                                    <td>${evaluation.id}</td>
                                    <td>${evaluation.employee_name}</td>
                                    <td>${evaluation.period}</td>
                                    <td><span class="badge badge-${evaluation.status}">${evaluation.status}</span></td>
                                    <td>${evaluation.created_at}</td>
                                    <td>
                                        <button class="btn btn-sm" onclick="app.viewEvaluation(${evaluation.id})">Ver</button>
                                        <button class="btn btn-sm" onclick="app.editEvaluation(${evaluation.id})">Editar</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async loadBonos() {
        const data = await this.apiRequest('/bonos/');
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Bonos de Desempeño</h2>
                    <button class="btn btn-primary" onclick="app.showBonoForm()">Nuevo Bono</button>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Empleado</th>
                                <th>Monto</th>
                                <th>Periodo</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.map(bono => `
                                <tr>
                                    <td>${bono.id}</td>
                                    <td>${bono.employee_name}</td>
                                    <td>$${bono.amount}</td>
                                    <td>${bono.period}</td>
                                    <td><span class="badge badge-${bono.status}">${bono.status}</span></td>
                                    <td>
                                        <button class="btn btn-sm" onclick="app.viewBono(${bono.id})">Ver</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async loadUsuarios() {
        const data = await this.apiRequest('/users/');
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Usuarios</h2>
                    <button class="btn btn-primary" onclick="app.showUserForm()">Nuevo Usuario</button>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Email</th>
                                <th>Rol</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.map(user => `
                                <tr>
                                    <td>${user.id}</td>
                                    <td>${user.name}</td>
                                    <td>${user.email}</td>
                                    <td>${user.role}</td>
                                    <td>${user.is_active ? 'Activo' : 'Inactivo'}</td>
                                    <td>
                                        <button class="btn btn-sm" onclick="app.editUser(${user.id})">Editar</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async loadReportes() {
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Reportes</h2>
                </div>
                <div class="reportes-grid">
                    <div class="reporte-item">
                        <h3>Reporte de Evaluaciones</h3>
                        <p>Genera un reporte completo de todas las evaluaciones del período.</p>
                        <button class="btn btn-primary" onclick="app.generateReport('evaluations')">Generar</button>
                    </div>
                    <div class="reporte-item">
                        <h3>Reporte de Bonos</h3>
                        <p>Reporte de bonos otorgados por período y área.</p>
                        <button class="btn btn-primary" onclick="app.generateReport('bonos')">Generar</button>
                    </div>
                    <div class="reporte-item">
                        <h3>Reporte de Rendimiento</h3>
                        <p>Análisis de rendimiento por empleado y departamento.</p>
                        <button class="btn btn-primary" onclick="app.generateReport('rendimiento')">Generar</button>
                    </div>
                </div>
            </div>
        `;
    }

    async loadAprobaciones() {
        const data = await this.apiRequest('/approvals/');
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Aprobaciones Pendientes</h2>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Tipo</th>
                                <th>Solicitante</th>
                                <th>Fecha</th>
                                <th>Monto</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.length === 0 ? '<tr><td colspan="6" style="text-align:center">No hay aprobaciones pendientes</td></tr>' : 
                            data.map(approval => `
                                <tr>
                                    <td>${approval.id}</td>
                                    <td>${approval.type}</td>
                                    <td>${approval.applicant_name}</td>
                                    <td>${approval.created_at}</td>
                                    <td>${approval.amount ? '$' + approval.amount : '-'}</td>
                                    <td>
                                        <button class="btn btn-success btn-sm" onclick="app.approveRequest(${approval.id})">Aprobar</button>
                                        <button class="btn btn-danger btn-sm" onclick="app.rejectRequest(${approval.id})">Rechazar</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async apiRequest(endpoint, options = {}) {
        const token = localStorage.getItem('auth_token');
        const url = CONFIG.API_BASE_URL + endpoint;
        
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            this.logout();
            throw new Error('Unauthorized');
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Error en la solicitud');
        }

        return response.json();
    }

    async login(username, password) {
        try {
            const response = await fetch(CONFIG.API_BASE_URL + '/auth/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error('Credenciales inválidas');
            }

            const data = await response.json();
            localStorage.setItem('auth_token', data.access);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            this.showToast('Login exitoso', 'success');
            this.showPage('dashboard');
        } catch (error) {
            this.showToast('Credenciales inválidas', 'error');
        }
    }

    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        this.showPage('login');
    }

    showLoading(show) {
        document.getElementById('loading').classList.toggle('hidden', !show);
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type}`;
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    showEvaluationForm() {
        console.log('Mostrar formulario de evaluación');
    }

    showBonoForm() {
        console.log('Mostrar formulario de bono');
    }

    showUserForm() {
        console.log('Mostrar formulario de usuario');
    }

    viewEvaluation(id) {
        console.log('Ver evaluación:', id);
    }

    editEvaluation(id) {
        console.log('Editar evaluación:', id);
    }

    viewBono(id) {
        console.log('Ver bono:', id);
    }

    editUser(id) {
        console.log('Editar usuario:', id);
    }

    generateReport(type) {
        console.log('Generar reporte:', type);
    }

    async approveRequest(id) {
        try {
            await this.apiRequest(`/approvals/${id}/approve/`, { method: 'POST' });
            this.showToast('Aprobación exitosa', 'success');
            this.showPage('aprobaciones');
        } catch (error) {
            this.showToast('Error al aprobar', 'error');
        }
    }

    async rejectRequest(id) {
        try {
            await this.apiRequest(`/approvals/${id}/reject/`, { method: 'POST' });
            this.showToast('Rechazado', 'success');
            this.showPage('aprobaciones');
        } catch (error) {
            this.showToast('Error al rechazar', 'error');
        }
    }
}

// Inicializar aplicación cuando el DOM esté listo
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ISAApp();

    document.addEventListener('submit', (e) => {
        if (e.target.id === 'login-form') {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            app.login(username, password);
        }
    });
});