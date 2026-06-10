const MSGraphService = {
    msalInstance: null,
    isInitialized: false,
    account: null,

    CONFIG: {
        clientId: 'TU_CLIENT_ID_AQUI',
        authority: 'https://login.microsoftonline.com/consumers',
        redirectUri: window.location.origin + '/',
        scopes: ['Files.ReadWrite.All']
    },

    init() {
        if (this.isInitialized) return Promise.resolve();
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://alcdn.msauth.net/browser/3.0.0/js/msal-browser.min.js';
            script.onload = () => {
                try {
                    this.msalInstance = new msal.PublicClientApplication({
                        auth: {
                            clientId: this.CONFIG.clientId,
                            authority: this.CONFIG.authority,
                            redirectUri: this.CONFIG.redirectUri
                        },
                        cache: { cacheLocation: 'localStorage' }
                    });
                    this.isInitialized = true;
                    resolve();
                } catch (e) {
                    reject(e);
                }
            };
            script.onerror = () => reject(new Error('No se pudo cargar MSAL.js'));
            document.head.appendChild(script);
        });
    },

    async login() {
        await this.init();
        try {
            const response = await this.msalInstance.loginPopup({
                scopes: this.CONFIG.scopes,
                prompt: 'select_account'
            });
            this.account = response.account;
            return response;
        } catch (e) {
            if (e.errorCode === 'user_cancelled') return null;
            throw e;
        }
    },

    async getToken() {
        await this.init();
        const accounts = this.msalInstance.getAllAccounts();
        if (accounts.length === 0) {
            await this.login();
        }
        const account = accounts[0] || this.account;
        if (!account) return null;
        try {
            const response = await this.msalInstance.acquireTokenSilent({
                scopes: this.CONFIG.scopes,
                account: account
            });
            this.account = response.account;
            return response.accessToken;
        } catch (e) {
            if (e.errorCode === 'consent_required' || e.errorCode === 'interaction_required') {
                const response = await this.msalInstance.acquireTokenPopup({
                    scopes: this.CONFIG.scopes,
                    account: account
                });
                this.account = response.account;
                return response.accessToken;
            }
            throw e;
        }
    },

    async isLoggedIn() {
        await this.init();
        const accounts = this.msalInstance.getAllAccounts();
        return accounts.length > 0;
    },

    async logout() {
        await this.init();
        this.account = null;
        await this.msalInstance.logoutPopup();
    },

    async getExcelWorksheetRange(fileId, sheetName, range) {
        const token = await this.getToken();
        if (!token) throw new Error('No autenticado');
        const url = `https://graph.microsoft.com/v1.0/me/drive/items/${fileId}/workbook/worksheets('${encodeURIComponent(sheetName)}')/range(address='${range}')`;
        const res = await fetch(url, {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error?.message || 'Error al leer el rango de Excel');
        }
        return res.json();
    },

    async updateExcelWorksheetRange(fileId, sheetName, range, values) {
        const token = await this.getToken();
        if (!token) throw new Error('No autenticado');
        const url = `https://graph.microsoft.com/v1.0/me/drive/items/${fileId}/workbook/worksheets('${encodeURIComponent(sheetName)}')/range(address='${range}')`;
        const res = await fetch(url, {
            method: 'PATCH',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ values: values })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error?.message || 'Error al escribir en el rango de Excel');
        }
        return res.json();
    }
};

window.MSGraphService = MSGraphService;
