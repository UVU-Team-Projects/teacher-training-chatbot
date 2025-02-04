/**********************************************
 * scenarioPicker.js
 * Handles creating a new session and listing existing sessions.
 * No backend calls — just placeholders for the future.
 **********************************************/

// We'll store sessions in localStorage under "chatSessions".
// Each session is: { id, scenario, style, tone }
let sessions = [];

/** Load existing sessions from localStorage */
function loadSessionsFromStorage() {
  const saved = localStorage.getItem("chatSessions");
  if (saved) {
    sessions = JSON.parse(saved);
  } else {
    sessions = [];
  }
}

/** Save sessions to localStorage */
function saveSessionsToStorage() {
  localStorage.setItem("chatSessions", JSON.stringify(sessions));
}

/** Render the session list in the #sessionList div */
function renderSessionList() {
  const sessionListDiv = document.getElementById("sessionList");
  sessionListDiv.innerHTML = "";

  if (sessions.length === 0) {
    sessionListDiv.innerHTML = "<p>No active sessions yet.</p>";
    return;
  }

  sessions.forEach((sess) => {
    const div = document.createElement("div");
    div.classList.add("session-item");
    div.textContent = `Scenario: ${sess.scenario} | Style: ${sess.style} | Tone: ${sess.tone}`;
    div.addEventListener("click", () => {
      // Open the chat page for this session
      localStorage.setItem("activeChatSessionId", sess.id);
      window.location.href = "chatPage.html";
    });
    sessionListDiv.appendChild(div);
  });
}

/** Create a new session from the form fields */
function createSession() {
  const scenario = document.getElementById("scenario").value;
  const style = document.getElementById("style").value;
  const tone = document.getElementById("tone").value;

  if (!scenario || !style || !tone) {
    alert("Please fill out all fields!");
    return;
  }

  // Build a new session object
  const newSession = {
    id: Date.now().toString(),
    scenario,
    style,
    tone
  };

  sessions.push(newSession);
  saveSessionsToStorage();

  // Also set this as the active session
  localStorage.setItem("activeChatSessionId", newSession.id);
  
  // Go to chat page
  window.location.href = "chatPage.html";
}

window.addEventListener("DOMContentLoaded", () => {
  // Load any existing sessions
  loadSessionsFromStorage();

  // Render them
  renderSessionList();

  // Attach event to "Start Chat" button
  const startBtn = document.getElementById("startChatBtn");
  startBtn.addEventListener("click", createSession);
});

