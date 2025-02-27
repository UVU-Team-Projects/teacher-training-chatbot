/**
 * Configuration file for API endpoints and utilities
 */
const API_BASE_URL = 'http://localhost:8000';

// API endpoint definitions
export const apiEndpoints = {
    students: `${API_BASE_URL}/students`,
    scenarios: `${API_BASE_URL}/scenarios`,
    chat: `${API_BASE_URL}/chat`,
    files: {
        active: `${API_BASE_URL}/files/active`,
        inactive: `${API_BASE_URL}/files/inactive`,
        moveToActive: (id) => `${API_BASE_URL}/files/move-to-active/${id}`,
        moveToInactive: (id) => `${API_BASE_URL}/files/move-to-inactive/${id}`
    }
};

// Base API fetch function
export async function fetchFromAPI(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(`API Error: ${response.status} - ${errorData}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Student-related API functions
 */
export const studentAPI = {
    async getAll() {
        return await fetchFromAPI(apiEndpoints.students);
    },

    async create(studentData) {
        return await fetchFromAPI(apiEndpoints.students, {
            method: 'POST',
            body: JSON.stringify(studentData)
        });
    }
};

/**
 * Scenario-related API functions
 */
export const scenarioAPI = {
    async getAll() {
        return await fetchFromAPI(apiEndpoints.scenarios);
    },

    async create(scenarioData) {
        return await fetchFromAPI(apiEndpoints.scenarios, {
            method: 'POST',
            body: JSON.stringify(scenarioData)
        });
    }
};

/**
 * Chat-related API functions
 */
export const chatAPI = {
    async sendMessage(message, sessionId) {
        return await fetchFromAPI(apiEndpoints.chat, {
            method: 'POST',
            body: JSON.stringify({ message, sessionId })
        });
    },

    async getResponses(sessionId) {
        return await fetchFromAPI(`${apiEndpoints.chat}/responses?sessionId=${sessionId}`);
    }
};

/**
 * File-related API functions
 */
export const fileAPI = {
    async getActiveFiles() {
        return await fetchFromAPI(apiEndpoints.files.active);
    },

    async getInactiveFiles() {
        return await fetchFromAPI(apiEndpoints.files.inactive);
    },

    async moveToActive(fileId) {
        return await fetchFromAPI(apiEndpoints.files.moveToActive(fileId), {
            method: 'PUT'
        });
    },

    async moveToInactive(fileId) {
        return await fetchFromAPI(apiEndpoints.files.moveToInactive(fileId), {
            method: 'PUT'
        });
    }
};