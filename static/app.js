/* ------------------------------------------------------------------
   Groq chatbot — front-end logic
   ------------------------------------------------------------------ */

const chatArea = document.getElementById("chat-area");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

/** Append a chat bubble to the message list and keep it scrolled down. */
function addMessage(role, text) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = role === "bot" ? "AI" : "Y";
    avatar.setAttribute("aria-hidden", "true");

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrapper.append(avatar, bubble);
    chatArea.appendChild(wrapper);
    chatArea.scrollTop = chatArea.scrollHeight;
    return bubble;
}

/** Enable / disable the form while a request is in flight. */
function setBusy(busy) {
    sendButton.disabled = busy;
    userInput.disabled = busy;
}

/** Send one message to /api/chat and show the reply. */
async function sendMessage(message) {
    addMessage("user", message);
    userInput.value = "";
    setBusy(true);

    const bubble = addMessage("bot", "");
    bubble.textContent = "Thinking";
    bubble.classList.add("typing");

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });

        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);

        bubble.textContent = data.reply;
        bubble.classList.remove("typing");
    } catch (err) {
        bubble.textContent = `Error: ${err.message}`;
        bubble.classList.remove("typing");
        bubble.classList.add("error");
    } finally {
        setBusy(false);
        userInput.focus();
    }
}

/** Restore the previous conversation from the server, if any. */
async function loadHistory() {
    try {
        const res = await fetch("/api/history");
        const data = await res.json();
        if (!res.ok || !Array.isArray(data.history)) return;

        if (data.history.length) {
            chatArea.innerHTML = "";
            data.history.forEach((msg) => addMessage(msg.role, msg.content));
        }
    } catch {
        /* keep the default welcome message */
    }
}

/* -- Wire up the form ------------------------------------------------ */
chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = userInput.value.trim();
    if (message) sendMessage(message);
});

/* -- Welcome message + restore previous history ----------------------- */
addMessage(
    "bot",
    "Welcome! I am the AI teaching assistant for Prof. Dr. Latifa Afrin " +
        "Dill Naher. Ask me a Physiology question, a teaching-related " +
        "question, or about her academic background."
);
loadHistory();
userInput.focus();