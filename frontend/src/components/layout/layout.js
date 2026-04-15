document.addEventListener("DOMContentLoaded", () => {
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
            <a href="../../admin/usuarios/usuarios.html" class="sidebar-link">
                <i class="bi bi-people fs-5"></i> Usuarios
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

    // 2. Inyectar tu HTML exacto, pero con las variables dinámicas
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
                    <span class="input-group-text bg-white border-end-0 border-light-subtle">
                        <i class="bi bi-search text-muted"></i>
                    </span>
                    <input type="text" class="form-control border-start-0 border-light-subtle bg-light" placeholder="Buscar datos de desempeño...">
                </div>
            </div>

            <div class="d-flex align-items-center gap-4">
                <div class="position-relative" style="cursor: pointer;">
                    <i class="bi bi-bell fs-5 text-secondary"></i>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem;">3</span>
                </div>
                
                <div class="d-flex align-items-center gap-2">
                    <div class="text-end d-none d-md-block">
                        <div class="fw-bold" style="font-size: 0.9rem;">${userData.nombre}</div>
                        <div class="text-muted text-capitalize" style="font-size: 0.8rem;">${userData.rol}</div>
                    </div>
                    <div class="rounded-circle bg-dark text-white d-flex justify-content-center align-items-center" style="width: 40px; height: 40px;">
                        <i class="bi bi-person fs-5"></i>
                    </div>
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="logout()">
                        <i class="bi bi-box-arrow-right"></i> Salir
                    </button>
                </div>
            </div>
        </nav>
    `;

    // 3. Activar el color azul en el menú donde el usuario está parado actualmente
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
        // Obtenemos el href y le quitamos los ../ para comparar con la URL actual
        const linkPath = link.getAttribute('href').replace(/\.\.\//g, '');
        if (currentPath.includes(linkPath)) {
            link.classList.add('active');
        }
    });
}