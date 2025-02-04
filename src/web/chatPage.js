/**********************************************
 * chatPage.js
 * Displays the chat for the currently active session.
 * No backend calls—bot just repeats scenario/style/tone for now.
 **********************************************/

let sessions = [];
let currentSession = null;

function loadSessionsFromStorage() {
  const saved = localStorage.getItem("chatSessions");
  if (saved) {
    sessions = JSON.parse(saved);
  } else {
    sessions = [];
  }
}

// Find the "activeChatSessionId" in localStorage
function loadActiveSession() {
  const activeId = localStorage.getItem("activeChatSessionId");
  if (!activeId) return;

  currentSession = sessions.find((s) => s.id === activeId);
}

// Render the chat interface
function renderChat() {
  const chatTitle = document.getElementById("chatTitle");
  const messagesDiv = document.getElementById("messages");

  if (!currentSession) {
    chatTitle.textContent = "No session active.";
    messagesDiv.innerHTML = "<p>No session found. Please go back.</p>";
    return;
  }

  // Show what scenario/style/tone we have
  chatTitle.textContent = `Chat - ${currentSession.scenario} (${currentSession.style}, ${currentSession.tone})`;

  // We'll store each "message" as an object: { sender: "teacher" or "student", text: "..."}
  // For now, let's keep it simple and store them in memory:
  // If you want to persist them, you'd add a chatLog array in currentSession.

  // We'll assume there's a local "chatLog" array in currentSession
  if (!currentSession.chatLog) {
    // Initialize if it doesn't exist
    currentSession.chatLog = [
      { sender: "student", text: `Hi teacher, I'm a student in a ${currentSession.scenario}!` }
    ];
  }

  messagesDiv.innerHTML = "";
  currentSession.chatLog.forEach((msg) => {
    const div = document.createElement("div");
    div.classList.add("message");
    if (msg.sender === "teacher") {
      div.classList.add("teacherMessage");
      div.textContent = `You: ${msg.text}`;
    } else if (msg.sender === "student") {
      div.classList.add("studentMessage");
      div.textContent = `Student: ${msg.text}`;
    } else {
      // bot
      div.classList.add("botMessage");
      div.textContent = `Bot: ${msg.text}`;
    }
    messagesDiv.appendChild(div);
  });

  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Handler for sending a teacher message
function sendTeacherMessage() {
  if (!currentSession) return;

  const textarea = document.getElementById("teacherMessage");
  const text = textarea.value.trim();
  if (!text) return;

  // Add teacher's message to chatLog
  currentSession.chatLog.push({
    sender: "teacher",
    text
  });

  // For now, the "bot" just repeats scenario, style, tone
  const scenario = currentSession.scenario;
  const style = currentSession.style;
  const tone = currentSession.tone;

  const botText = `I see the scenario is "${scenario}", style is "${style}", and tone is "${tone}".`;
  currentSession.chatLog.push({
    sender: "bot",
    text: botText
  });

  // Clear text area
  textarea.value = "";

  // Re-render
  renderChat();
  // Save updated chatLog so we don't lose it on refresh
  saveSessionsToStorage();
}

// Save sessions to localStorage again
function saveSessionsToStorage() {
  localStorage.setItem("chatSessions", JSON.stringify(sessions));
}

// Setup event listeners
window.addEventListener("DOMContentLoaded", () => {
  // Load all sessions + active session
  loadSessionsFromStorage();
  loadActiveSession();

  // Render chat
  renderChat();

  // "Send" button
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.addEventListener("click", sendTeacherMessage);

  // "Back to Scenario Picker"
  const backBtn = document.getElementById("backBtn");
  backBtn.addEventListener("click", () => {
    window.location.href = "scenarioPicker.html";
  });
});

