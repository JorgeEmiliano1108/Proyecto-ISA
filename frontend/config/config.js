// Configuración del sistema
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api',
    PAGES: {
        login: 'login',
        dashboard: 'dashboard',
        evaluations: 'evaluations',
        bonos: 'bonos',
        usuarios: 'usuarios',
        reportes: 'reportes',
        aprobaciones: 'aprobaciones'
    }
};

// Exportar para uso global
window.ISA_CONFIG = CONFIG;