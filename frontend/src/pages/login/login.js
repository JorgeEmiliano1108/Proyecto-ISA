document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    // SIMULACIÓN DE BACKEND:
    // Aquí es donde en el futuro harás: fetch('api/login', {method: 'POST', body: ...})
    
    if(user === 'admin') {
        window.location.href = './src/pages/admin/dashboard/dashboard.html';
    } else {
        window.location.href = './src/pages/usuario/dashboard/dashboard.html';
    }
});