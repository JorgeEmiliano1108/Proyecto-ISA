document.addEventListener("DOMContentLoaded", () => {
    // --- 0. APLICAR TEMA DINÁMICO (Agregado) ---
    const savedColor = localStorage.getItem('isaThemeColor');
    if (savedColor) {
        document.documentElement.style.setProperty('--primary-color', savedColor);
    }

    const container = document.getElementById('layout-container');
    const userData = JSON.parse(localStorage.getItem('userData'));

    // Redirigir al login si no hay sesión
    if (!userData) {
        window.location.href = '../../../../index.html'; 
        return;
    }

    const isAdmin = userData.rol === 'admin';

    // 1. Crear los enlaces dinámicos según el rol
    let sidebarLinks = "";

    if (isAdmin) {
        sidebarLinks = `
            <a href="../../admin/dashboard/dashboard.html" class="sidebar-link">
                <i class="bi bi-grid-1x2 fs-5"></i> Dashboard
            </a>
            <a href="../../admin/usuarios/usuarios.html" class="sidebar-link">
                <i class="bi bi-people fs-5"></i> Usuarios
            </a>
            <a href="../../admin/catalogos/catalogos.html" class="sidebar-link">
                <i class="bi bi-folder2-open fs-5"></i> Catálogos
            </a>
            <a href="../../admin/evaluaciones/evaluaciones.html" class="sidebar-link">
                <i class="bi bi-ui-checks fs-5"></i> Evaluaciones
            </a>
            <a href="../../admin/aprobaciones/aprobaciones.html" class="sidebar-link">
                <i class="bi bi-patch-check fs-5"></i> Aprobaciones
            </a>
            <a href="../../admin/reportes/reportes.html" class="sidebar-link">
                <i class="bi bi-bar-chart fs-5"></i> Reportes
            </a>
            <a href="../../admin/bonos/bonos.html" class="sidebar-link">
                <i class="bi bi-cash-stack fs-5"></i> Bonos
            </a>
        `;
    } else {
        sidebarLinks = `
            <a href="../../usuario/dashboard/dashboard.html" class="sidebar-link">
                <i class="bi bi-grid-1x2 fs-5"></i> Mi Resumen
            </a>
            <a href="../../usuario/evaluaciones/evaluaciones.html" class="sidebar-link">
                <i class="bi bi-ui-checks fs-5"></i> Mis Evaluaciones
            </a>
            <a href="../../usuario/bonos/bonos.html" class="sidebar-link">
                <i class="bi bi-cash-stack fs-5"></i> Mis Bonos
            </a>
            <a href="../../usuario/reportes/reportes.html" class="sidebar-link">
                <i class="bi bi-bar-chart fs-5"></i> Mis Reportes
            </a>
        `;
    }

    // 2. Inyectar tu HTML con la Navbar Mejorada
    container.innerHTML = `
        <aside class="sidebar shadow-sm">
            <div class="sidebar-logo text-center">
                <h4 class="fw-bold mb-0">ISA</h4>
                <h5 class="fw-bold mb-0">CORPORATIVO</h5>
                <p class="text-muted mt-1" style="font-size: 0.8rem;">Sistema de Gestión</p>
            </div>
            
            <div class="nav flex-column mt-4">
                ${sidebarLinks}
            </div>
        </aside>

        <nav class="top-navbar shadow-sm">
            <div class="d-flex align-items-center w-50">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 border-light-subtle px-3">
                        <i class="bi bi-search text-muted"></i>
                    </span>
                    <input type="text" class="form-control border-start-0 border-light-subtle bg-light" placeholder="Buscar datos de desempeño...">
                </div>
            </div>

            <div class="d-flex align-items-center gap-4">
                
                <div class="d-flex align-items-center gap-4 text-secondary" style="cursor: pointer;">
                    <div class="position-relative hover-icon">
                        <i class="bi bi-bell fs-5 text-dark"></i>
                        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem; padding: 0.3em 0.5em;">3</span>
                    </div>
                    <div class="hover-icon d-none d-sm-block"><i class="bi bi-gear fs-5 text-dark"></i></div>
                    <div class="hover-icon d-none d-sm-block"><i class="bi bi-question-circle fs-5 text-dark"></i></div>
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
                        <li><a class="dropdown-item py-2 small" href="#"><i class="bi bi-person me-2 text-muted"></i> Mi Perfil</a></li>
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
});

// Función para cerrar sesión
function logout() {
    localStorage.removeItem('userData');
    window.location.href = '../../../../index.html';
}

// Función extra: Marca el menú actual como activo
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