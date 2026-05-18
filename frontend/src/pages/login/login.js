const API_BASE_URL = 'http://localhost:8000/api/v1';

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

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const btn = e.target.querySelector('.btn-login');
    btn.innerHTML = 'Validando...';
    btn.style.opacity = '0.7';
    btn.style.pointerEvents = 'none';

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Credenciales inválidas');
        }

        const data = await res.json();

        const payload = JSON.parse(atob(data.access.split('.')[1]));

        const rol = payload.rol_id === 5 ? 'admin' : 'usuario';

        const userData = {
            nombre: payload.nombre_completo,
            username: payload.username,
            rol: rol,
            puesto: payload.puesto,
            user_id: payload.user_id,
            departamento_id: payload.departamento_id
        };

        localStorage.setItem('userData', JSON.stringify(userData));
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);

        window.location.href = rol === 'admin'
            ? './src/pages/admin/dashboard/dashboard.html'
            : './src/pages/usuario/dashboard/dashboard.html';

    } catch (err) {
        alert('Error: ' + err.message);
        btn.innerHTML = 'Iniciar Sesión';
        btn.style.opacity = '1';
        btn.style.pointerEvents = 'auto';
    }
});