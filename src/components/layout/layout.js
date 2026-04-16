document.addEventListener("DOMContentLoaded", () => {
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
            <a href="../../admin/dashboard/dashboard.html" class="sidebar-link"><i class="bi bi-grid-1x2 fs-5"></i> Dashboard</a>
            <a href="../../admin/evaluaciones/evaluaciones.html" class="sidebar-link"><i class="bi bi-ui-checks fs-5"></i> Evaluaciones</a>
            <a href="../../admin/aprobaciones/aprobaciones.html" class="sidebar-link"><i class="bi bi-patch-check fs-5"></i> Aprobaciones</a>
            <a href="../../admin/reportes/reportes.html" class="sidebar-link"><i class="bi bi-bar-chart fs-5"></i> Reportes</a>
            <a href="../../admin/bonos/bonos.html" class="sidebar-link"><i class="bi bi-cash-stack fs-5"></i> Bonos</a>
            <a href="../../admin/usuarios/usuarios.html" class="sidebar-link"><i class="bi bi-people fs-5"></i> Usuarios</a>
        `;
    } else {
        sidebarLinks = `
            <a href="../../usuario/dashboard/dashboard.html" class="sidebar-link"><i class="bi bi-grid-1x2 fs-5"></i> Mi Resumen</a>
            <a href="../../usuario/evaluaciones/evaluaciones.html" class="sidebar-link"><i class="bi bi-ui-checks fs-5"></i> Mis Evaluaciones</a>
            <a href="../../usuario/bonos/bonos.html" class="sidebar-link"><i class="bi bi-cash-stack fs-5"></i> Mis Bonos</a>
            <a href="../../usuario/reportes/reportes.html" class="sidebar-link"><i class="bi bi-bar-chart fs-5"></i> Mis Reportes</a>
        `;
    }

    container.innerHTML = `
        <aside class="sidebar shadow-sm">
            <div class="sidebar-logo text-center">
                <h4 class="fw-bold mb-0">ISA</h4>
                <h5 class="fw-bold mb-0">CORPORATIVO</h5>
                <p class="text-muted mt-1" style="font-size: 0.8rem;">Sistema de Gestión</p>
            </div>
            <div class="nav flex-column mt-4">${sidebarLinks}</div>
        </aside>

        <nav class="top-navbar shadow-sm">
            <div class="d-flex align-items-center w-50">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 border-light-subtle"><i class="bi bi-search text-muted"></i></span>
                    <input type="text" class="form-control border-start-0 border-light-subtle bg-light" placeholder="Buscar datos de desempeño...">
                </div>
            </div>

            <div class="d-flex align-items-center gap-4">
                <div class="notification-container me-2">
                    <i class="bi bi-bell fs-5 text-secondary"></i>
                    <span class="badge rounded-pill bg-danger">3</span>
                </div>
                
                <div class="dropdown">
                    <div class="d-flex align-items-center gap-2 profile-trigger" role="button" id="profileMenu" data-bs-toggle="dropdown" aria-expanded="false">
                        <div class="text-end d-none d-md-block">
                            <div class="fw-bold" style="font-size: 0.9rem;">${userData.nombre}</div>
                            <div class="text-muted text-capitalize" style="font-size: 0.8rem;">${userData.rol}</div>
                        </div>
                        <div class="rounded-circle bg-dark text-white d-flex justify-content-center align-items-center" style="width: 40px; height: 40px;">
                            <i class="bi bi-person fs-5"></i>
                        </div>
                    </div>

                    <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0" aria-labelledby="profileMenu">
                        <li><h6 class="dropdown-header">Opciones</h6></li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <button class="dropdown-item text-danger d-flex align-items-center gap-2" onclick="logout()">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    `;

    marcarLinkActivo();
});

function logout() {
    localStorage.removeItem('userData');
    window.location.href = '../../../../index.html';
}

function marcarLinkActivo() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.sidebar-link');
    links.forEach(link => {
        const linkPath = link.getAttribute('href').replace(/\.\.\//g, '');
        if (currentPath.includes(linkPath)) { link.classList.add('active'); }
    });
}