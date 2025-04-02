document.addEventListener("DOMContentLoaded", () => {
    loadActiveChats();

    document.getElementById("newChatBtn").addEventListener("click", () => {
        window.location.href = "scenarioPicker.html";
    });
});

function loadActiveChats() {
    const chatListDiv = document.getElementById("chatList");
    chatListDiv.innerHTML = "";

    const chats = JSON.parse(localStorage.getItem("chatSessions")) || [];
    chats.sort((a, b) => b.timestamp - a.timestamp);

    if (chats.length === 0) {
        chatListDiv.innerHTML = "<p>No active chats.</p>";
        return;
    }

    chats.forEach(chat => {
        const chatItem = document.createElement("div");
        chatItem.classList.add("chat-item");

        const chatText = document.createElement("span");
        chatText.textContent = `${chat.student} - ${chat.scenario}`;
        chatText.addEventListener("click", () => {
            localStorage.setItem("activeChatSessionId", chat.id);
            window.location.href = "chatPage.html";
        });

        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";
        deleteBtn.classList.add("delete-btn");
        deleteBtn.addEventListener("click", (event) => {
            event.stopPropagation(); // Prevent click from opening the chat
            deleteChat(chat.id);
        });

        chatItem.appendChild(chatText);
        chatItem.appendChild(deleteBtn);
        chatListDiv.appendChild(chatItem);
    });
}

function deleteChat(chatId) {
    let chats = JSON.parse(localStorage.getItem("chatSessions")) || [];
    chats = chats.filter(chat => chat.id !== chatId);
    localStorage.setItem("chatSessions", JSON.stringify(chats));
    loadActiveChats(); // Refresh the list
}
