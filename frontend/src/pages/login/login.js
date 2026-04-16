document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value; // Aquí validarás con el backend después

    // Creamos el objeto de sesión
    const userData = {
        nombre: user,
        rol: user === 'admin' ? 'admin' : 'usuario'
    };

    // Guardamos en LocalStorage para que el Layout sepa qué mostrar
    localStorage.setItem('userData', JSON.stringify(userData));

    // REDIRECCIÓN LÓGICA
    if(user === 'admin') {
        // El admin va a su dashboard
        window.location.href = './src/pages/admin/dashboard/dashboard.html';
    } else {
        // EL USUARIO DEBE IR A SU DASHBOARD, NO AL LAYOUT
        // Esta es la ruta correcta según tu árbol de carpetas:
        window.location.href = './src/pages/usuario/dashboard/dashboard.html';
    }
});