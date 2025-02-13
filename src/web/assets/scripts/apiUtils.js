const API_BASE_URL = "https://your-api-endpoint.com"; // Replace with actual API URL

/**
 * Fetches the list of default students from the API.
 * @returns {Promise<Array>} A promise that resolves to an array of students.
 */
async function fetchStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/students`);
        if (!response.ok) throw new Error("Failed to fetch students");
        return await response.json();
    } catch (error) {
        console.error("Error fetching students:", error);
        return [];
    }
}

/**
 * Fetches the list of default scenarios from the API.
 * @returns {Promise<Array>} A promise that resolves to an array of scenarios.
 */
async function fetchScenarios() {
    try {
        const response = await fetch(`${API_BASE_URL}/scenarios`);
        if (!response.ok) throw new Error("Failed to fetch scenarios");
        return await response.json();
    } catch (error) {
        console.error("Error fetching scenarios:", error);
        return [];
    }
}

/**
 * Sends a message to the AI.
 * @param {string} sessionId - The active chat session ID.
 * @param {string} message - The message text to send.
 * @returns {Promise<Object>} A promise that resolves to the AI's response.
 */
async function sendMessageToAI(sessionId, message) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sessionId, message }),
        });
        if (!response.ok) throw new Error("Failed to send message");
        return await response.json();
    } catch (error) {
        console.error("Error sending message:", error);
        return null;
    }
}

/**
 * Fetches AI responses for the active chat session.
 * @param {string} sessionId - The active chat session ID.
 * @returns {Promise<Array>} A promise that resolves to an array of chat messages.
 */
async function fetchAIResponses(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/responses?sessionId=${sessionId}`);
        if (!response.ok) throw new Error("Failed to fetch AI responses");
        return await response.json();
    } catch (error) {
        console.error("Error fetching AI responses:", error);
        return [];
    }
}

/**
 * Fetches the list of documents and their active status.
 * @returns {Promise<Array>} A promise that resolves to an array of documents.
 */
async function fetchDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/documents`);
        if (!response.ok) throw new Error("Failed to fetch documents");
        return await response.json();
    } catch (error) {
        console.error("Error fetching documents:", error);
        return [];
    }
}

/**
 * Sends a list of documents to be set as active or revectorized.
 * @param {Array<string>} documentIds - Array of document IDs to activate/revectorize.
 * @returns {Promise<boolean>} A promise that resolves to a boolean indicating success.
 */
async function setActiveDocuments(documentIds) {
    try {
        const response = await fetch(`${API_BASE_URL}/documents/activate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ documentIds }),
        });
        if (!response.ok) throw new Error("Failed to update document status");
        return true;
    } catch (error) {
        console.error("Error updating document status:", error);
        return false;
    }
}

export {
    fetchStudents,
    fetchScenarios,
    sendMessageToAI,
    fetchAIResponses,
    fetchDocuments,
    setActiveDocuments,
};
