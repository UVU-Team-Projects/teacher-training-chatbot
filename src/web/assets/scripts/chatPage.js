import { chatAPI, fileAPI } from './apiUtils.js';

/**
 * Global state variables for chat functionality
 */
let currentChat = null;  // Stores current chat session
let activeFiles = [];    // Stores list of active files
let inactiveFiles = []; // Stores list of inactive files
let selectedDocuments = new Set(); // Stores selected document IDs

/**
 * Initialize the chat page when DOM is loaded
 */
document.addEventListener("DOMContentLoaded", async () => {
    try {
        await loadFiles();
        await loadAndInitializeChat();
        setupEventListeners();
    } catch (error) {
        console.error('Error initializing chat page:', error);
    }
});

/**
 * Load active and inactive files from the API
 */
async function loadFiles() {
    try {
        activeFiles = await fileAPI.getActiveFiles();
        inactiveFiles = await fileAPI.getInactiveFiles();
        updateDocumentList();
    } catch (error) {
        console.error('Error loading files:', error);
    }
}

function updateDocumentList() {
    const documentList = document.getElementById("documentList");
    documentList.innerHTML = "";

    [...activeFiles, ...inactiveFiles].forEach(file => {
        const fileDiv = createDocumentElement(file, activeFiles.includes(file));
        documentList.appendChild(fileDiv);
    });
}

function createDocumentElement(file, isActive) {
    const fileDiv = document.createElement("div");
    fileDiv.classList.add("document-item");
    if (selectedDocuments.has(file.id)) {
        fileDiv.classList.add("selected");
    }

    const statusDot = document.createElement("span");
    statusDot.classList.add("status-dot");
    if (isActive) statusDot.classList.add("active");

    const fileName = document.createElement("span");
    fileName.textContent = file.name;

    fileDiv.appendChild(statusDot);
    fileDiv.appendChild(fileName);

    fileDiv.addEventListener("click", () => toggleDocumentSelection(file.id));

    return fileDiv;
}

function toggleDocumentSelection(fileId) {
    if (selectedDocuments.has(fileId)) {
        selectedDocuments.delete(fileId);
    } else {
        selectedDocuments.add(fileId);
    }
    updateDocumentList();
}

async function handleActivateDocuments() {
    try {
        for (const fileId of selectedDocuments) {
            await fileAPI.moveToActive(fileId);
        }
        selectedDocuments.clear();
        await loadFiles(); // Refresh the list
    } catch (error) {
        console.error('Error activating documents:', error);
        alert('Failed to activate selected documents');
    }
}

/**
 * Set up all event listeners for the chat interface
 */
function setupEventListeners() {
    // Navigation event listener
    document.getElementById("backBtn").addEventListener("click", () => {
        window.location.href = "index.html";
    });

    // Message input event listeners
    const messageInput = document.getElementById("teacherMessage");
    const sendBtn = document.getElementById("sendBtn");

    messageInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    sendBtn.addEventListener("click", handleSendMessage);

    document.getElementById("activateBtn").addEventListener("click", handleActivateDocuments);
}

/**
 * Load and initialize the chat session from local storage
 */
async function loadAndInitializeChat() {
    const sessionId = localStorage.getItem("activeChatSessionId");
    if (!sessionId) {
        window.location.href = "index.html";
        return;
    }

    // Load chat session from local storage
    const sessions = JSON.parse(localStorage.getItem("chatSessions")) || [];
    currentChat = sessions.find(s => s.id === sessionId);

    if (!currentChat) {
        window.location.href = "index.html";
        return;
    }

    // Update UI with chat information
    document.getElementById("chatTitle").textContent = 
        `Chat with ${currentChat.student} - ${currentChat.scenario}`;

    // Display chat history and handle initial message
    displayChatHistory();
    if (currentChat.chatLog.length === 1) {
        const initialMessage = currentChat.chatLog[0].text;
        await getAIResponse(initialMessage);
    }
}

/**
 * Display all messages in the chat history
 */
function displayChatHistory() {
    const messages = document.getElementById("messages");
    messages.innerHTML = "";
    
    currentChat.chatLog.forEach(msg => {
        addMessageToChat(msg.sender, msg.text);
    });
}

/**
 * Handle sending a new message
 */
async function handleSendMessage() {
    const messageInput = document.getElementById("teacherMessage");
    const message = messageInput.value.trim();
    
    if (!message) return;

    addMessageToChat("user", message);
    saveMessageToHistory("user", message);
    messageInput.value = "";
    
    await getAIResponse(message);
}

/**
 * Get response from AI API
 * @param {string} message - Message to send to AI
 */
async function getAIResponse(message) {
    try {
        const response = await chatAPI.sendMessage(message, currentChat.id);
        addMessageToChat("ai", response.response);
        saveMessageToHistory("ai", response.response);
    } catch (error) {
        console.error("Error getting AI response:", error);
        addMessageToChat("system", "Failed to get AI response");
        saveMessageToHistory("system", "Failed to get AI response");
    }
}

/**
 * Add a message to the chat UI
 * @param {string} sender - Message sender (user/ai/system)
 * @param {string} text - Message content
 */
function addMessageToChat(sender, text) {
    const messages = document.getElementById("messages");
    if (!messages) {
        console.error('Messages element not found');
        return;
    }
    
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    
    const textContent = document.createElement("p");
    textContent.textContent = text;
    
    messageDiv.appendChild(textContent);
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

/**
 * Save message to local storage
 * @param {string} sender - Message sender
 * @param {string} text - Message content
 */
function saveMessageToHistory(sender, text) {
    currentChat.chatLog.push({
        sender,
        text,
        timestamp: new Date().toISOString()
    });

    // Update local storage with new message
    const sessions = JSON.parse(localStorage.getItem("chatSessions")) || [];
    const index = sessions.findIndex(s => s.id === currentChat.id);
    if (index !== -1) {
        sessions[index] = currentChat;
        localStorage.setItem("chatSessions", JSON.stringify(sessions));
    }
}
