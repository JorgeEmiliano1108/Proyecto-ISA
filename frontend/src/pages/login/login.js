// --- Lógica del selector de color ---
const picker = document.getElementById('colorPicker');

window.addEventListener('DOMContentLoaded', () => {
    const savedColor = localStorage.getItem('isaThemeColor');
    if (savedColor) {
        document.documentElement.style.setProperty('--primary-color', savedColor);
        picker.value = savedColor;
    }
});

picker.addEventListener('input', (e) => {
    const color = e.target.value;
    document.documentElement.style.setProperty('--primary-color', color);
    localStorage.setItem('isaThemeColor', color);
});

// --- Tu lógica original de login ---
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const btn = e.target.querySelector('.btn-login');
    
    // Efecto de carga visual
    btn.innerHTML = 'Validando...';
    btn.style.opacity = '0.7';
    btn.style.pointerEvents = 'none';

    const user = document.getElementById('username').value;

    const userData = {
        nombre: user,
        rol: user === 'admin' ? 'admin' : 'usuario'
    };

    localStorage.setItem('userData', JSON.stringify(userData));

    // Simulamos una pequeña espera para la animación
    setTimeout(() => {
        if(user === 'admin') {
            window.location.href = './src/pages/admin/dashboard/dashboard.html';
        } else {
            window.location.href = './src/pages/usuario/dashboard/dashboard.html';
        }
    }, 800);
});