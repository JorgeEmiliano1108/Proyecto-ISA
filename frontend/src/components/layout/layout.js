document.addEventListener("DOMContentLoaded", () => {
    const layoutContainer = document.getElementById('layout-container');

    if (layoutContainer) {
        // Hacemos una petición (fetch) para traer el HTML de nuestro layout
        fetch('/frontend/src/components/layout/layout.html')
            .then(response => {
                if (!response.ok) throw new Error("No se pudo cargar el layout");
                return response.text();
            })
            .then(html => {
                // 1. Inyectamos el HTML en el contenedor
                layoutContainer.innerHTML = html;
                
                // 2. Activamos la clase visual de la página actual
                marcarMenuActivo();
                
                // 3. Le damos funcionalidad al botón de salir
                configurarLogout();
            })
            .catch(error => console.error('Error cargando el layout:', error));
    }
});

// Función para saber en qué página estamos y pintar el botón del menú de azul
function marcarMenuActivo() {
    const pathActual = window.location.pathname;
    const links = document.querySelectorAll('.sidebar-link');

    links.forEach(link => {
        const href = link.getAttribute('href');
        // Si la ruta actual coincide con el href del enlace, le ponemos la clase 'active'
        if (pathActual.includes(href)) {
            link.classList.add('active');
        }
    });
}

// Función para simular el cierre de sesión
function configurarLogout() {
    const btnLogout = document.getElementById('btnLogout');
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            // Cuando haya backend, aquí irá el fetch al endpoint de logout.
            // Por ahora, solo redirigimos al login principal.
            window.location.href = '/frontend/index.html';
        });
    }
}