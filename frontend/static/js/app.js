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
        try {
            const token = localStorage.getItem('auth_token');
            const userData = localStorage.getItem('user_data');
            
            if (!token || !userData) {
                this.showPage('login');
            } else {
                this.currentUser = JSON.parse(userData);
                this.updateHeader(true);
                this.showPage('dashboard');
            }
        } catch (e) {
            console.error('Auth check error:', e);
            this.showPage('login');
        }
    }

    updateHeader(isLoggedIn) {
        const header = document.getElementById('app-header');
        const logoutBtn = document.getElementById('logout-btn');
        const userName = document.getElementById('user-name');
        const userAvatar = document.getElementById('user-avatar');
        
        if (header) {
            header.style.display = isLoggedIn ? 'flex' : 'none';
        }
        if (logoutBtn) {
            logoutBtn.style.display = isLoggedIn ? 'flex' : 'none';
        }
        if (userName && this.currentUser) {
            userName.textContent = this.currentUser.full_name || this.currentUser.username;
        }
        if (userAvatar && this.currentUser) {
            const firstLetter = (this.currentUser.first_name || this.currentUser.username || 'U').charAt(0).toUpperCase();
            userAvatar.textContent = firstLetter;
        }
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                this.showPage(page);
            }

            if (e.target.closest('#logout-btn')) {
                this.logout();
            }
        });

        document.addEventListener('submit', (e) => {
            if (e.target.id === 'login-form') {
                e.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                this.login(username, password);
            }
        });
    }

    async showPage(page) {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;
        
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
        } catch (error) {
            console.error('Error loading page:', error);
            mainContent.innerHTML = '<div class="alert alert-danger">Error al cargar la página</div>';
        } finally {
            this.showLoading(false);
        }
    }

    renderLogin() {
        return `
        <div class="login-container">
            <div class="login-box">
                <div class="login-logo">
                    <div class="login-logo-icon">ISA</div>
                    <h1>Corporativo ISA</h1>
                    <p>Sistema de Gestión de Evaluaciones</p>
                </div>
                <form id="login-form" class="login-form">
                    <div class="login-input-group">
                        <label for="username">Usuario</label>
                        <i class="bi bi-person login-input-icon"></i>
                        <input type="text" class="login-input" id="username" placeholder="Ingrese su usuario" required>
                    </div>
                    <div class="login-input-group">
                        <label for="password">Contraseña</label>
                        <i class="bi bi-lock login-input-icon"></i>
                        <input type="password" class="login-input" id="password" placeholder="Ingrese su contraseña" required>
                    </div>
                    <button type="submit" class="login-btn">
                        <i class="bi bi-box-arrow-in-right"></i> Iniciar Sesión
                    </button>
                </form>
            </div>
        </div>`;
    }

    async loadDashboard() {
        try {
            const data = await this.apiRequest('/evaluations/dashboard/');
            return `
            <div class="dashboard-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-clipboard-data"></i></div>
                    <div class="stat-value">${data.total_evaluations || 0}</div>
                    <div class="stat-label">Total Evaluaciones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-clock-history"></i></div>
                    <div class="stat-value">${data.pending || 0}</div>
                    <div class="stat-label">Pendientes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-check-circle"></i></div>
                    <div class="stat-value">${data.approved || 0}</div>
                    <div class="stat-label">Aprobadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-x-circle"></i></div>
                    <div class="stat-value">${data.rejected || 0}</div>
                    <div class="stat-label">Rechazadas</div>
                </div>
            </div>`;
        } catch (e) {
            return '<div class="alert alert-warning">No hay datos disponibles</div>';
        }
    }

    async loadEvaluations() {
        try {
            const data = await this.apiRequest('/evaluations/');
            if (!data || data.length === 0) {
                return `<div class="card"><div class="card-header"><h2><i class="bi bi-clipboard-check"></i> Evaluaciones</h2></div><div class="card-body text-center text-muted p-4">No hay evaluaciones registradas</div></div>`;
            }
            let rows = data.map(function(evalItem) {
                let statusClass = 'draft';
                if (evalItem.status === 'approved') statusClass = 'approved';
                else if (evalItem.status === 'rejected') statusClass = 'rejected';
                else if (evalItem.status === 'pending') statusClass = 'pending';
                
                return `<tr>
                    <td><strong>#${evalItem.id}</strong></td>
                    <td>${evalItem.employee_name || 'N/A'}</td>
                    <td>${evalItem.period}</td>
                    <td><span class="badge badge-${statusClass}">${evalItem.status}</span></td>
                    <td>${evalItem.created_at ? evalItem.created_at.substring(0, 10) : '-'}</td>
                    <td><button class="btn btn-primary btn-sm"><i class="bi bi-eye"></i></button></td>
                </tr>`;
            }).join('');
            return `<div class="card">
                <div class="card-header">
                    <h2><i class="bi bi-clipboard-check"></i> Evaluaciones</h2>
                    <button class="btn btn-primary"><i class="bi bi-plus-lg"></i> Nueva</button>
                </div>
                <div class="card-body p-0">
                    <table class="table"><thead><tr><th>ID</th><th>Empleado</th><th>Periodo</th><th>Estado</th><th>Fecha</th><th>Acción</th></tr></thead><tbody>${rows}</tbody></table>
                </div>
            </div>`;
        } catch (e) {
            return '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error al cargar evaluaciones</div>';
        }
    }

    async loadBonos() {
        try {
            const data = await this.apiRequest('/bonos/');
            if (!data || data.length === 0) {
                return `<div class="card"><div class="card-header"><h2><i class="bi bi-gift"></i> Bonos de Desempeño</h2></div><div class="card-body text-center text-muted p-4">No hay bonos registrados</div></div>`;
            }
            let rows = data.map(function(bono) {
                let statusClass = 'pending';
                if (bono.status === 'approved') statusClass = 'approved';
                else if (bono.status === 'rejected') statusClass = 'rejected';
                
                return `<tr>
                    <td><strong>#${bono.id}</strong></td>
                    <td>${bono.employee_name || 'N/A'}</td>
                    <td><strong>$${parseFloat(bono.amount).toLocaleString()}</strong></td>
                    <td>${bono.period}</td>
                    <td><span class="badge badge-${statusClass}">${bono.status}</span></td>
                </tr>`;
            }).join('');
            return `<div class="card">
                <div class="card-header">
                    <h2><i class="bi bi-gift"></i> Bonos de Desempeño</h2>
                    <button class="btn btn-primary"><i class="bi bi-plus-lg"></i> Nuevo</button>
                </div>
                <div class="card-body p-0">
                    <table class="table"><thead><tr><th>ID</th><th>Empleado</th><th>Monto</th><th>Periodo</th><th>Estado</th></tr></thead><tbody>${rows}</tbody></table>
                </div>
            </div>`;
        } catch (e) {
            return '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error al cargar bonos</div>';
        }
    }

    async loadUsuarios() {
        try {
            const data = await this.apiRequest('/users/');
            if (!data || data.length === 0) {
                return `<div class="card"><div class="card-header"><h2><i class="bi bi-people"></i> Usuarios</h2></div><div class="card-body text-center text-muted p-4">No hay usuarios</div></div>`;
            }
            let rows = data.map(function(user) {
                const roles = user.groups ? user.groups.join(', ') : 'Sin rol';
                return `<tr>
                    <td><strong>${user.id}</strong></td>
                    <td>${user.full_name}</td>
                    <td>${user.email}</td>
                    <td><span class="badge badge-info">${roles}</span></td>
                    <td>${user.is_active ? '<span class="badge badge-approved">Activo</span>' : '<span class="badge badge-rejected">Inactivo</span>'}</td>
                </tr>`;
            }).join('');
            return `<div class="card">
                <div class="card-header">
                    <h2><i class="bi bi-people"></i> Usuarios</h2>
                    <button class="btn btn-primary"><i class="bi bi-plus-lg"></i> Nuevo</button>
                </div>
                <div class="card-body p-0">
                    <table class="table"><thead><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Estado</th></tr></thead><tbody>${rows}</tbody></table>
                </div>
            </div>`;
        } catch (e) {
            return '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error al cargar usuarios</div>';
        }
    }

    async loadReportes() {
        return `<div class="card">
            <div class="card-header">
                <h2><i class="bi bi-file-earmark-bar-graph"></i> Reportes</h2>
            </div>
            <div class="card-body">
                <div class="reportes-grid">
                    <div class="reporte-item">
                        <i class="bi bi-clipboard-data" style="font-size: 2rem; color: var(--accent); margin-bottom: 1rem;"></i>
                        <h3>Reporte de Evaluaciones</h3>
                        <p>Genera un reporte completo de todas las evaluaciones del período</p>
                        <button class="btn btn-primary"><i class="bi bi-download"></i> Generar</button>
                    </div>
                    <div class="reporte-item">
                        <i class="bi bi-gift" style="font-size: 2rem; color: var(--success); margin-bottom: 1rem;"></i>
                        <h3>Reporte de Bonos</h3>
                        <p>Reporte de bonos otorgados por período y área</p>
                        <button class="btn btn-primary"><i class="bi bi-download"></i> Generar</button>
                    </div>
                    <div class="reporte-item">
                        <i class="bi bi-graph-up" style="font-size: 2rem; color: var(--warning); margin-bottom: 1rem;"></i>
                        <h3>Reporte de Rendimiento</h3>
                        <p>Análisis de rendimiento por empleado y departamento</p>
                        <button class="btn btn-primary"><i class="bi bi-download"></i> Generar</button>
                    </div>
                </div>
            </div>
        </div>`;
    }

    async loadAprobaciones() {
        try {
            const data = await this.apiRequest('/approvals/');
            if (!data || data.length === 0) {
                return `<div class="card"><div class="card-header"><h2><i class="bi bi-check-circle"></i> Aprobaciones</h2></div><div class="card-body text-center text-muted p-4">No hay aprobaciones pendientes</div></div>`;
            }
            let rows = data.map(function(approval) {
                return `<tr>
                    <td><strong>#${approval.id}</strong></td>
                    <td><span class="badge badge-info">${approval.request_type}</span></td>
                    <td>${approval.requested_by_name || 'N/A'}</td>
                    <td><span class="badge badge-${approval.status}">${approval.status}</span></td>
                    <td>
                        <button class="btn btn-success btn-sm"><i class="bi bi-check"></i></button>
                        <button class="btn btn-danger btn-sm"><i class="bi bi-x"></i></button>
                    </td>
                </tr>`;
            }).join('');
            return `<div class="card">
                <div class="card-header">
                    <h2><i class="bi bi-check-circle"></i> Aprobaciones Pendientes</h2>
                </div>
                <div class="card-body p-0">
                    <table class="table"><thead><tr><th>ID</th><th>Tipo</th><th>Solicitante</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>${rows}</tbody></table>
                </div>
            </div>`;
        } catch (e) {
            return '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error al cargar aprobaciones</div>';
        }
    }

    async apiRequest(endpoint, options) {
        options = options || {};
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        const response = await fetch(CONFIG.API_BASE_URL + endpoint, {
            method: options.method || 'GET',
            headers: headers,
            body: options.body
        });

        if (response.status === 401) {
            this.logout();
            throw new Error('Unauthorized');
        }

        if (!response.ok) {
            throw new Error('Error en la solicitud');
        }

        return response.json();
    }

    async login(username, password) {
        try {
            const response = await fetch(CONFIG.API_BASE_URL + '/auth/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username, password: password })
            });

            if (!response.ok) {
                throw new Error('Credenciales inválidas');
            }

            const data = await response.json();
            localStorage.setItem('auth_token', data.access);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            this.currentUser = data.user;
            
            this.updateHeader(true);
            this.showPage('dashboard');
        } catch (error) {
            alert('Credenciales inválidas. Por favor verifique su usuario y contraseña.');
        }
    }

    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        this.currentUser = null;
        this.updateHeader(false);
        this.showPage('login');
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            if (show) {
                loading.classList.remove('hidden');
            } else {
                loading.classList.add('hidden');
            }
        }
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    window.app = new ISAApp();
});