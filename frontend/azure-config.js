// Azure configuration for frontend
const AZURE_CONFIG = {
    // Using local backend for now due to Azure quota limits
    FUNCTION_APP_URL: 'http://localhost:8000',
    SEARCH_ENDPOINT: 'http://localhost:9200',
    STORAGE_ENDPOINT: 'https://nasaweatherstorage3896.blob.core.windows.net',
    
    // API endpoints
    ENDPOINTS: {
        PREDICT: '/predict',
        SEARCH: '/search',
        HEALTH: '/health'
    }
};

// API helper functions
const AzureAPI = {
    async predict(date, hour = 12, location = null) {
        try {
            const response = await fetch(`${AZURE_CONFIG.FUNCTION_APP_URL}${AZURE_CONFIG.ENDPOINTS.PREDICT}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date,
                    hour,
                    location
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Prediction API error:', error);
            throw error;
        }
    },

    async search(query, filters = {}) {
        try {
            const params = new URLSearchParams({
                q: query,
                ...filters
            });
            
            const response = await fetch(`${AZURE_CONFIG.FUNCTION_APP_URL}${AZURE_CONFIG.ENDPOINTS.SEARCH}?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Search API error:', error);
            throw error;
        }
    },

    async healthCheck() {
        try {
            const response = await fetch(`${AZURE_CONFIG.FUNCTION_APP_URL}${AZURE_CONFIG.ENDPOINTS.HEALTH}`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', error: error.message };
        }
    }
};

// Export for use in other files
window.AzureAPI = AzureAPI;
window.AZURE_CONFIG = AZURE_CONFIG;