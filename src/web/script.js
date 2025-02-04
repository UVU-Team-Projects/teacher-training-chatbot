/***************************************
 * Boilerplate class for AI connection *
 ***************************************/
class AIReceiver {
    /**
     * Placeholder method for sending a user message to the AI backend
     */
    sendMessageToAI(userMessage) {
      console.log("Sending to AI backend (placeholder):", userMessage);
      // TODO: Implement actual network request to AI backend in the future
    }
  
    /**
     * Placeholder method for receiving a message (response) from the AI backend
     * For now, it just returns "Hi, my name is {botName}"
     */
    receiveMessageFromAI(botName) {
      return `Hi, my name is ${botName}.`;
    }
  }
  
  // Our 6 bots (shared across sessions)
  const bots = ["Bob", "Steve", "Alice", "Lucy", "Mark", "John"];
  
  /******************************************
   * Multi-Session Data Model:
   * sessions = {
   *   [sessionId]: {
   *     name: string,
   *     chatHistory: [ {sender, text, timestamp} ],
   *     currentBot: string | null
   *   },
   *   ...
   * }
   ******************************************/
  let sessions = {};
  let currentSessionId = null;
  
  // Try loading sessions from localStorage
  const savedSessions = localStorage.getItem("chatSessions");
  if (savedSessions) {
    sessions = JSON.parse(savedSessions);
  }
  
  // We'll generate a simple numeric or date-based ID for new sessions
  function generateSessionId() {
    return Date.now().toString();
  }
  
  /******************************************
   * DOM Elements
   ******************************************/
  const newSessionBtn = document.getElementById("newSessionBtn");
  const sessionListUl = document.getElementById("session-list");
  const botListUl = document.getElementById("bot-list");
  
  const themeToggle = document.getElementById("themeToggle");
  const clearChatBtn = document.getElementById("clearChatBtn");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const messagesContainer = document.getElementById("messages");
  const sessionTitle = document.getElementById("sessionTitle");
  
  /******************************************
   * Bot Colors (Light & Dark Variants)
   ******************************************/
  const botColors = {
    Bob:   { light: "#fbc8c8", dark: "#b26b6b" },
    Steve: { light: "#c8fbc8", dark: "#6ca66c" },
    Alice: { light: "#c8dbfb", dark: "#6b7bb2" },
    Lucy:  { light: "#fce8b0", dark: "#b2a15f" },
    Mark:  { light: "#fbc8f7", dark: "#b26ba9" },
    John:  { light: "#c8f7fb", dark: "#6ba3b2" },
  };
  
  /******************************************
   * AI Receiver
   ******************************************/
  const aiReceiver = new AIReceiver();
  
  /******************************************
   * On Page Load
   ******************************************/
  document.addEventListener("DOMContentLoaded", () => {
    renderSessionsList();
    populateBotList();
  });
  
  /******************************************
   * 1) Sessions Handling
   ******************************************/
  
  // Create a new session
  newSessionBtn.addEventListener("click", () => {
    const sessionName = prompt("Enter a session name:", "New Session");
    if (!sessionName) return; // user cancelled or empty
  
    // Build a new session object
    const sessionId = generateSessionId();
    sessions[sessionId] = {
      name: sessionName.trim(),
      chatHistory: [],
      currentBot: null,
    };
  
    // Save to localStorage
    saveSessionsToStorage();
  
    // Update UI
    renderSessionsList();
  
    // Auto-select the new session
    selectSession(sessionId);
  });
  
  /**
   * Render all existing sessions in the sidebar
   */
  function renderSessionsList() {
    sessionListUl.innerHTML = "";
  
    Object.entries(sessions).forEach(([id, sessionData]) => {
      const li = document.createElement("li");
      li.textContent = sessionData.name;
      li.dataset.sessionId = id;
  
      // Highlight if it's the currently selected session
      if (id === currentSessionId) {
        li.classList.add("selected");
      }
  
      sessionListUl.appendChild(li);
    });
  }
  
  /**
   * When the user clicks on a session in the sidebar
   */
  sessionListUl.addEventListener("click", (e) => {
    if (e.target.tagName === "LI") {
      const sessionId = e.target.dataset.sessionId;
      selectSession(sessionId);
    }
  });
  
  /**
   * Select a session and load its chat
   */
  function selectSession(sessionId) {
    currentSessionId = sessionId;
  
    // Highlight in the UI
    const allLis = sessionListUl.querySelectorAll("li");
    allLis.forEach((li) => {
      li.classList.remove("selected");
      if (li.dataset.sessionId === sessionId) {
        li.classList.add("selected");
      }
    });
  
    // Update heading
    sessionTitle.textContent = sessions[sessionId].name;
  
    // If the session has a currentBot, set it
    // (We'll highlight that bot in the bot list below)
    const { currentBot } = sessions[sessionId];
  
    // Show chat history
    renderChatHistory(sessionId);
  
    // Update the bot list highlight
    highlightSelectedBot(currentBot);
  
    // Enable or disable input based on whether a bot is selected
    if (currentBot) {
      userInput.disabled = false;
      userInput.placeholder = `Send messages to ${currentBot}...`;
    } else {
      userInput.disabled = true;
      userInput.placeholder = `Select a bot...`;
    }
  }
  
  /**
   * Render the conversation for a specific session
   */
  function renderChatHistory(sessionId) {
    messagesContainer.innerHTML = "";
    const { chatHistory } = sessions[sessionId];
    chatHistory.forEach((msg) => {
      appendMessageToUI(msg.sender, msg.text);
    });
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  /**
   * Save all sessions to localStorage
   */
  function saveSessionsToStorage() {
    localStorage.setItem("chatSessions", JSON.stringify(sessions));
  }
  
  /******************************************
   * 2) Bot Selection
   ******************************************/
  function populateBotList() {
    bots.forEach((bot) => {
      const li = document.createElement("li");
      li.textContent = bot;
      li.dataset.botName = bot;
      botListUl.appendChild(li);
    });
  }
  
  // Clicking on a bot in the list
  botListUl.addEventListener("click", (e) => {
    if (!currentSessionId) return; // No session selected
    if (e.target.tagName === "LI") {
      const selectedBot = e.target.dataset.botName;
  
      // Update session's currentBot
      sessions[currentSessionId].currentBot = selectedBot;
      saveSessionsToStorage();
  
      highlightSelectedBot(selectedBot);
  
      // Enable input
      userInput.disabled = false;
      userInput.placeholder = `Send messages to ${selectedBot}...`;
    }
  });
  
  function highlightSelectedBot(botName) {
    const allLis = botListUl.querySelectorAll("li");
    allLis.forEach((li) => {
      li.classList.remove("selected");
      if (li.dataset.botName === botName) {
        li.classList.add("selected");
      }
    });
  }
  
  /******************************************
   * 3) Light/Dark Mode
   ******************************************/
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    // Re-apply bot bubble colors in case user toggles mid-session
    reapplyBotColors();
  });
  
  /******************************************
   * 4) Clearing Chat
   ******************************************/
  clearChatBtn.addEventListener("click", () => {
    if (!currentSessionId) return;
    // Empty that session's chat history
    sessions[currentSessionId].chatHistory = [];
    saveSessionsToStorage();
    messagesContainer.innerHTML = "";
  });
  
  /******************************************
   * 5) Chat Form Submission
   ******************************************/
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
  
    if (!currentSessionId) return; // No session chosen
    const currentSession = sessions[currentSessionId];
    if (!currentSession.currentBot) return; // No bot chosen
  
    const message = userInput.value.trim();
    if (!message) return;
  
    // 1. Add user's message
    addMessageToSession(currentSessionId, "User", message);
  
    // 2. Send to AIReceiver (placeholder)
    aiReceiver.sendMessageToAI(message);
  
    // 3. Bot responds
    const botResponse = aiReceiver.receiveMessageFromAI(currentSession.currentBot);
  
    // 4. Add bot's message
    addMessageToSession(currentSessionId, currentSession.currentBot, botResponse);
  
    // 5. Clear input
    userInput.value = "";
  });
  
  /******************************************
   * Helper Functions
   ******************************************/
  
  /**
   * Add a message to the session's chat history, append to UI, save
   */
  function addMessageToSession(sessionId, sender, text) {
    const newMsg = {
      sender,
      text,
      timestamp: new Date().toISOString(),
    };
  
    sessions[sessionId].chatHistory.push(newMsg);
    saveSessionsToStorage();
  
    appendMessageToUI(sender, text);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  /**
   * Create message HTML elements and append to #messages
   */
  function appendMessageToUI(sender, text) {
    const messageDiv = document.createElement("div");
    const className = sender === "User" ? "user-message" : "bot-message";
    messageDiv.classList.add("message", className);
  
    // Bot color
    if (sender !== "User" && botColors[sender]) {
      applyBotColor(messageDiv, sender);
    }
  
    const nameDiv = document.createElement("div");
    nameDiv.classList.add("message-name");
    nameDiv.textContent = sender;
  
    const textDiv = document.createElement("div");
    textDiv.classList.add("message-text");
    textDiv.textContent = text;
  
    messageDiv.appendChild(nameDiv);
    messageDiv.appendChild(textDiv);
    messagesContainer.appendChild(messageDiv);
  }
  
  /**
   * Dynamically apply the bot's color, choosing light or dark variant
   */
  function applyBotColor(element, botName) {
    const isDark = document.body.classList.contains("dark");
    const colorKey = isDark ? "dark" : "light";
    const backgroundColor = botColors[botName][colorKey];
    const textColor = isDark ? "#f1f1f1" : "#2b2b2b";
  
    element.style.backgroundColor = backgroundColor;
    element.style.color = textColor;
  }
  
  /**
   * Re-apply color to all existing .bot-message elements in the chat
   * when toggling light/dark mid-session
   */
  function reapplyBotColors() {
    const messageDivs = messagesContainer.querySelectorAll(".bot-message");
    messageDivs.forEach((div) => {
      const senderName = div.querySelector(".message-name")?.textContent;
      if (senderName && botColors[senderName]) {
        applyBotColor(div, senderName);
      }
    });
  }
  
