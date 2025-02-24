document.addEventListener("DOMContentLoaded", () => {
    loadChat();
    loadDocuments();

    document.getElementById("sendBtn").addEventListener("click", sendMessage);
    document.getElementById("teacherMessage").addEventListener("keypress", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    document.getElementById("backBtn").addEventListener("click", () => {
        window.location.href = "index.html";
    });

    document.getElementById("activateBtn").addEventListener("click", activateSelectedDocuments);
});

// Sample document list (to be replaced with database fetching)
let documents = [
    { id: 1, name: "Introduction to AI", active: false, selected: false },
    { id: 2, name: "Neural Networks Explained", active: false, selected: false },
    { id: 3, name: "Data Science Handbook", active: false, selected: false },
    { id: 4, name: "Large Language Models", active: false, selected: false },
    { id: 5, name: "Natural Language Processing", active: false, selected: false },
    { id: 6, name: "Deep Learning for Dummies", active: false, selected: false },
    { id: 7, name: "Vector Embeddings 101", active: false, selected: false },
    { id: 8, name: "The Mathematics of ML", active: false, selected: false },
    { id: 9, name: "AI Ethics and Fairness", active: false, selected: false },
    { id: 10, name: "Deploying AI in Production", active: false, selected: false }
];

function loadDocuments() {
    const documentList = document.getElementById("documentList");
    documentList.innerHTML = "";

    documents.forEach(doc => {
        const docItem = document.createElement("div");
        docItem.classList.add("document-item");
        docItem.dataset.id = doc.id;

        // Highlight selected documents
        if (doc.selected) {
            docItem.classList.add("selected");
        }

        // Document active status indicator
        const statusIndicator = document.createElement("span");
        statusIndicator.classList.add("document-status");
        statusIndicator.textContent = doc.active ? "🟢" : "⚪";

        // Document name
        const docName = document.createElement("span");
        docName.textContent = doc.name;

        // Click selection for activation
        docItem.addEventListener("click", () => toggleDocumentSelection(doc.id));
        
        docItem.appendChild(docName);
        docItem.appendChild(statusIndicator);
        documentList.appendChild(docItem);
    });
}

function toggleDocumentSelection(docId) {
    let doc = documents.find(d => d.id === docId);
    if (doc) {
        doc.selected = !doc.selected;
        loadDocuments();
    }
}

function activateSelectedDocuments() {
    // Set all documents inactive first
    documents.forEach(doc => doc.active = false);

    // Activate only selected ones
    documents.forEach(doc => {
        if (doc.selected) {
            doc.active = true;
            doc.selected = false; // Reset selection after activation
        }
    });

    loadDocuments(); // Refresh UI
}

/* ==========================
   CHAT FUNCTIONALITY
============================= */

function loadChat() {
    const activeId = localStorage.getItem("activeChatSessionId");
    const sessions = JSON.parse(localStorage.getItem("chatSessions")) || [];
    const session = sessions.find(s => s.id === activeId);

    if (!session) return;

    document.getElementById("chatTitle").textContent = `Chat with ${session.student}`;

    // Ensure the scenario description is the first message
    if (!session.chatLog || session.chatLog.length === 0) {
        session.chatLog = [{ sender: "student", text: session.scenario }];
        saveSessionsToStorage(sessions);
    }

    renderChat(session);
}

function sendMessage() {
    const messageInput = document.getElementById("teacherMessage");
    const messageText = messageInput.value.trim();

    if (!messageText) return;

    const activeId = localStorage.getItem("activeChatSessionId");
    let sessions = JSON.parse(localStorage.getItem("chatSessions")) || [];
    let session = sessions.find(s => s.id === activeId);

    if (!session) return;

    // Add teacher message
    session.chatLog.push({ sender: "teacher", text: messageText });

    // Simulated bot response (Optional)
    const botResponse = generateBotResponse(session);
    if (botResponse) {
        session.chatLog.push({ sender: "bot", text: botResponse });
    }

    saveSessionsToStorage(sessions);
    renderChat(session);

    messageInput.value = "";
}

function generateBotResponse(session) {
    return `Hmm, interesting! You’re in a "${session.scenario}" situation. Let's discuss.`;
}

function renderChat(session) {
    const messagesDiv = document.getElementById("messages");
    messagesDiv.innerHTML = "";

    session.chatLog.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");
        if (msg.sender === "teacher") {
            messageDiv.classList.add("teacherMessage");
            messageDiv.textContent = `You: ${msg.text}`;
        } else if (msg.sender === "student") {
            messageDiv.classList.add("studentMessage");
            messageDiv.textContent = `Student: ${msg.text}`;
        } else {
            messageDiv.classList.add("botMessage");
            messageDiv.textContent = `Bot: ${msg.text}`;
        }
        messagesDiv.appendChild(messageDiv);
    });

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function saveSessionsToStorage(sessions) {
    localStorage.setItem("chatSessions", JSON.stringify(sessions));
}
