document.addEventListener("DOMContentLoaded", () => {
    const savedColor = localStorage.getItem('isaThemeColor');
    if (savedColor) {
        document.documentElement.style.setProperty('--primary-color', savedColor);
    }

    const container = document.getElementById('layout-container');
    const userData = JSON.parse(localStorage.getItem('userData'));

    if (!userData) {
        window.location.href = '../../../../index.html'; 
        return;
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
                            <div class="fw-bold text-dark" style="font-size: 0.9rem; line-height: 1.2;">${userData.nombre}</div>
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