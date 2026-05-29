const API_BASE_URL = 'http://localhost:8000/api/v1';

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
}

function isTokenExpired() {
    const token = localStorage.getItem('access_token');
    if (!token) return true;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    } catch {
        return true;
    }
}

async function tryRefreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });
        if (!res.ok) return false;
        const data = await res.json();
        localStorage.setItem('access_token', data.access);
        if (data.refresh) {
            localStorage.setItem('refresh_token', data.refresh);
        }
        return true;
    } catch {
        return false;
    }
}

async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = { ...options, headers: { ...getAuthHeaders(), ...options.headers } };
    let res = await fetch(url, config);
    if (res.status === 401) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            config.headers = { ...getAuthHeaders(), ...options.headers };
            res = await fetch(url, config);
        } else {
            logout();
            throw new Error('Sesión expirada');
        }
    }
    return res;
}

document.addEventListener("DOMContentLoaded", async () => {
    const savedColor = localStorage.getItem('isaThemeColor');
    if (savedColor) {
        document.documentElement.style.setProperty('--primary-color', savedColor);
    }

    const container = document.getElementById('layout-container');
    let userData = JSON.parse(localStorage.getItem('userData'));

    if (!userData) {
        window.location.href = '../../../../index.html'; 
        return;
    }

    if (localStorage.getItem('refresh_token') && isTokenExpired()) {
        const refreshed = await tryRefreshToken();
        if (!refreshed) {
            logout();
            return;
        }
    }

    const isAdmin = userData.rol === 'admin';

    let sidebarLinks = "";

    if (isAdmin) {
        sidebarLinks = `
            <a href="../../admin/dashboard/dashboard.html" class="sidebar-link">
                <i class="bi bi-grid-1x2"></i> <span class="link-text">Dashboard</span>
            </a>
            <a href="../../admin/usuarios/usuarios.html" class="sidebar-link">
                <i class="bi bi-people"></i> <span class="link-text">Usuarios</span>
            </a>
            <a href="../../admin/catalogos/catalogos.html" class="sidebar-link">
                <i class="bi bi-folder2-open"></i> <span class="link-text">Catálogos</span>
            </a>
            <a href="../../admin/evaluaciones/evaluaciones.html" class="sidebar-link">
                <i class="bi bi-ui-checks"></i> <span class="link-text">Evaluaciones</span>
            </a>
            <a href="../../admin/aprobaciones/aprobaciones.html" class="sidebar-link">
                <i class="bi bi-patch-check"></i> <span class="link-text">Aprobaciones</span>
            </a>
            <a href="../../admin/reportes/reportes.html" class="sidebar-link">
                <i class="bi bi-bar-chart"></i> <span class="link-text">Reportes</span>
            </a>
            <a href="../../admin/bonos/bonos.html" class="sidebar-link">
                <i class="bi bi-cash-stack"></i> <span class="link-text">Bonos</span>
            </a>
            <a href="../../admin/configuracion/configuracion.html" class="sidebar-link">
                <i class="bi bi-palette fs-5"></i> Configuración
            </a>
            <a href="../../admin/consultas/consultas.html" class="sidebar-link">
                <i class="bi bi-chat-dots"></i> <span class="link-text">Aclaraciones</span>
            </a>
        `;
    } else {
        sidebarLinks = `
            <a href="../../usuario/dashboard/dashboard.html" class="sidebar-link">
                <i class="bi bi-grid-1x2"></i> <span class="link-text">Mi Resumen</span>
            </a>
            <a href="../../usuario/evaluaciones/evaluaciones.html" class="sidebar-link">
                <i class="bi bi-ui-checks"></i> <span class="link-text">Mis Evaluaciones</span>
            </a>
            <a href="../../usuario/bonos/bonos.html" class="sidebar-link">
                <i class="bi bi-cash-stack"></i> <span class="link-text">Mis Bonos</span>
            </a>
            <a href="../../usuario/reportes/reportes.html" class="sidebar-link">
                <i class="bi bi-bar-chart"></i> <span class="link-text">Mis Reportes</span>
            </a>
        `;
    }

    container.innerHTML = `
        <aside class="sidebar shadow-sm">
            <div class="sidebar-logo">
                <h4 class="fw-bold mb-0">ISA</h4>
                <h4 class="fw-bold mb-0 logo-corp">CORPORATIVO</h4>
            </div>
            
            <div class="nav flex-column mt-2">
                ${sidebarLinks}
            </div>
        </aside>

        <nav class="top-navbar shadow-sm">
            <div class="d-flex align-items-center w-50 gap-3">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 border-light-subtle px-3">
                        <i class="bi bi-search text-muted"></i>
                    </span>
                    <input type="text" class="form-control border-start-0 border-light-subtle bg-light" placeholder="Buscar datos de desempeño...">
                </div>
            </div>

            <div class="d-flex align-items-center gap-4">
                
                <div class="d-flex align-items-center gap-4 text-secondary" style="cursor: pointer;">
                    <div id="navbar-notificaciones"></div>
                    <div class="hover-icon" onclick="abrirModalPerfil()"><i class="bi bi-gear fs-5 text-dark"></i></div>
                    <div id="navbar-ayuda"></div>
                </div>
                
                <div class="vr d-none d-md-block mx-2" style="height: 35px; align-self: center; background-color: #dee2e6; width: 2px;"></div>

                <div class="dropdown">
                    <div class="d-flex align-items-center gap-3" data-bs-toggle="dropdown" aria-expanded="false" style="cursor: pointer;">
                        <div class="text-end d-none d-md-block">
                            <div class="fw-bold text-dark" style="font-size: 0.9rem; line-height: 1.2;">${userData.nombre || userData.username}</div>
                            <div class="text-muted text-capitalize" style="font-size: 0.8rem;">${userData.rol}</div>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <div class="rounded-circle bg-dark text-white d-flex justify-content-center align-items-center shadow-sm" style="width: 42px; height: 42px;">
                                <i class="bi bi-person fs-5"></i>
                            </div>
                            <i class="bi bi-chevron-down text-muted d-none d-md-block" style="font-size: 0.8rem;"></i>
                        </div>
                    </div>
                    
                    <ul class="dropdown-menu dropdown-menu-end shadow border-0 mt-3" style="min-width: 180px; border-radius: 10px;">
                        <li><h6 class="dropdown-header text-uppercase" style="font-size: 0.7rem;">Mi Cuenta</h6></li>
                        <li><a class="dropdown-item py-2 small" href="#" onclick="abrirModalPerfil(); return false;"><i class="bi bi-person me-2 text-muted"></i> Mi Perfil</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <button class="dropdown-item text-danger fw-bold py-2 small" onclick="logout()">
                                <i class="bi bi-box-arrow-right me-2"></i> Cerrar Sesión
                            </button>
                        </li>
                    </ul>
                </div>

            </div>
        </nav>
    `;

    marcarLinkActivo();
    initNavBarIcons(isAdmin);
});

function initNavBarIcons(isAdmin) {
    if (isAdmin) {
        document.getElementById('navbar-notificaciones').innerHTML = `
            <div class="position-relative hover-icon" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false" style="cursor: pointer;" onclick="marcarLeidasNotif()">
                <i class="bi bi-bell fs-5 text-dark"></i>
                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem; padding: 0.3em 0.5em; display: ${getNoLeidas() > 0 ? 'block' : 'none'};">${getNoLeidas()}</span>
            </div>
        `;
        
        document.getElementById('navbar-ayuda').innerHTML = `
            <div class="hover-icon d-none d-sm-block" onclick="window.location.href='../../admin/consultas/consultas.html'">
                <i class="bi bi-question-circle fs-5 text-dark" title="Aclaraciones"></i>
            </div>
        `;
        
        const dropdownNotif = document.createElement('div');
        dropdownNotif.className = 'dropdown-menu dropdown-menu-end shadow border-0 mt-3';
        dropdownNotif.style.cssText = 'width: 350px; max-height: 400px; overflow-y: auto; border-radius: 10px;';
        dropdownNotif.id = 'dropdown-nav-notif';
        dropdownNotif.innerHTML = typeof renderNotificacionesDropdown === 'function' ? renderNotificacionesDropdown() : '';
        document.getElementById('navbar-notificaciones').appendChild(dropdownNotif);
    } else {
        if(typeof renderNotificacionesDropdown === 'function') {
            document.getElementById('navbar-notificaciones').innerHTML = renderNotificacionesDropdown();
        }
        if(typeof renderDropdownAyuda === 'function') {
            document.getElementById('navbar-ayuda').innerHTML = renderDropdownAyuda();
        }
    }
}

function getNoLeidas() {
    const data = localStorage.getItem('isa_notificaciones');
    const notifs = data ? JSON.parse(data) : [];
    return notifs.filter(n => !n.leido).length;
}

function marcarLeidasNotif() {
    const data = localStorage.getItem('isa_notificaciones');
    if (data) {
        const notifs = JSON.parse(data);
        let cambio = false;
        notifs.forEach(n => { if (!n.leido) { n.leido = true; cambio = true; } });
        if (cambio) localStorage.setItem('isa_notificaciones', JSON.stringify(notifs));
    }
}

function logout() {
    localStorage.removeItem('userData');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '../../../../index.html';
}

function marcarLinkActivo() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.sidebar-link');
    
    links.forEach(link => {
        const linkPath = link.getAttribute('href').replace(/\.\.\//g, '');
        if (currentPath.includes(linkPath)) {
            link.classList.add('active');
        }
    });
}