/* ------------------------------------------------------------------
   Groq chatbot — front-end logic
   ------------------------------------------------------------------ */

const chatArea = document.getElementById("chat-area");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

const panelToggle = document.getElementById("panel-toggle");
const panelBody = document.getElementById("panel-body");
const tabPubBtn = document.getElementById("tab-pub-btn");
const tabMeuBtn = document.getElementById("tab-meu-btn");
const tabBspBtn = document.getElementById("tab-bsp-btn");
const tabPublications = document.getElementById("tab-publications");
const tabMeu = document.getElementById("tab-meu");
const tabBsp = document.getElementById("tab-bsp");

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

/* ------------------------------------------------------------------
   Knowledge panel: Research publications (journal name + volume) and
   MEU activities (Member Secretary & Coordinator, UMC).
   ------------------------------------------------------------------ */

/** Toggle the collapsible knowledge panel. */
function initPanelToggle() {
    panelToggle.addEventListener("click", () => {
        const isOpen = !panelBody.hidden;
        panelBody.hidden = isOpen;
        panelToggle.setAttribute("aria-expanded", String(!isOpen));
        panelToggle.textContent = isOpen ? "Show details ▾" : "Hide details ▴";
    });
}

/** Switch between the Publications, MEU and BSP tabs. */
function initTabs() {
    const show = (which) => {
        const isPub = which === "pub";
        const isMeu = which === "meu";
        const isBsp = which === "bsp";
        tabPublications.hidden = !isPub;
        tabMeu.hidden = !isMeu;
        tabBsp.hidden = !isBsp;
        tabPubBtn.classList.toggle("active", isPub);
        tabMeuBtn.classList.toggle("active", isMeu);
        tabBspBtn.classList.toggle("active", isBsp);
        tabPubBtn.setAttribute("aria-selected", String(isPub));
        tabMeuBtn.setAttribute("aria-selected", String(isMeu));
        tabBspBtn.setAttribute("aria-selected", String(isBsp));
    };
    tabPubBtn.addEventListener("click", () => show("pub"));
    tabMeuBtn.addEventListener("click", () => show("meu"));
    tabBspBtn.addEventListener("click", () => show("bsp"));
}

/** Render each publication as a small card with journal + volume details. */
function renderPublications(pubs) {
    tabPublications.innerHTML = "";
    const list = document.createElement("ul");
    list.className = "pub-list";

    pubs.forEach((p) => {
        const item = document.createElement("li");
        item.className = "pub-card";

        const title = document.createElement("strong");
        title.textContent = p.title;

        const meta = document.createElement("span");
        meta.className = "pub-meta";
        meta.textContent =
            `${p.authors} · ${p.journal_short}, ` +
            `${p.year}; Vol. ${p.volume}, No. ${p.issue}: pp. ${p.pages}.`;

        const doi = document.createElement("a");
        doi.className = "pub-doi";
        doi.href = p.url || `https://doi.org/${p.doi}`;
        doi.target = "_blank";
        doi.rel = "noopener noreferrer";
        doi.textContent = `DOI: ${p.doi}`;

        item.append(title, meta, doi);
        list.appendChild(item);
    });

    tabPublications.appendChild(list);
}

/** Render the MEU role summary and activity list. */
function renderMeu(meu) {
    tabMeu.innerHTML = "";

    const role = document.createElement("p");
    role.className = "meu-role";
    role.textContent = `${meu.title} · ${meu.unit} · ${meu.institution}`;

    const summary = document.createElement("p");
    summary.className = "meu-summary";
    summary.textContent = meu.summary;

    const list = document.createElement("ul");
    list.className = "meu-list";
    (meu.activities || []).forEach((activity) => {
        const li = document.createElement("li");
        li.textContent = activity;
        list.appendChild(li);
    });

    tabMeu.append(role, summary, list);
}

/** Render the BSP role summary, activities and CME training. */
function renderBsp(bsp) {
    tabBsp.innerHTML = "";

    const role = document.createElement("p");
    role.className = "meu-role";
    role.textContent = `${bsp.title} · ${bsp.society}`;

    const summary = document.createElement("p");
    summary.className = "meu-summary";
    summary.textContent = bsp.summary;

    const list = document.createElement("ul");
    list.className = "meu-list";
    (bsp.activities || []).forEach((activity) => {
        const li = document.createElement("li");
        li.textContent = activity;
        list.appendChild(li);
    });

    tabBsp.append(role, summary, list);

    if (bsp.training) {
        const trainingTitle = document.createElement("p");
        trainingTitle.className = "meu-role training-title";
        trainingTitle.textContent = "🎓 CME Training & Faculty Development";

        const trainingList = document.createElement("ul");
        trainingList.className = "meu-list";
        const t1 = document.createElement("li");
        t1.textContent =
            `Completed “${bsp.training.program}” training (${bsp.training.organizer}).`;
        const t2 = document.createElement("li");
        t2.textContent = bsp.training.outcome;
        trainingList.append(t1, t2);

        tabBsp.append(trainingTitle, trainingList);
    }
}

/** Load the publications, MEU and BSP data from the API and render them. */
async function loadKnowledge() {
    try {
        const [pubRes, meuRes, bspRes] = await Promise.all([
            fetch("/api/publications"),
            fetch("/api/meu"),
            fetch("/api/bsp"),
        ]);
        const pubData = await pubRes.json().catch(() => ({ publications: [] }));
        const meuData = await meuRes.json().catch(() => ({ activities: [] }));
        const bspData = await bspRes
            .json()
            .catch(() => ({ activities: [], training: null }));
        renderPublications(pubData.publications || []);
        renderMeu(meuData);
        renderBsp(bspData);
    } catch {
        tabPublications.textContent = "Publications could not be loaded.";
        tabMeu.textContent = "MEU activities could not be loaded.";
        tabBsp.textContent = "BSP role could not be loaded.";
    }
}

/** Wire up the quick-reply suggestion chips. */
function initSuggestions() {
    document.querySelectorAll(".chip").forEach((chip) => {
        chip.addEventListener("click", () => {
            const question = chip.dataset.question;
            if (question) sendMessage(question);
        });
    });
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
        "Dill Naher. Ask me a Physiology question, her research " +
        "publications (journal name with volume number), her activities as " +
        "Vice President of the BSP Dhaka Division, or her MEU activities " +
        "and teacher training at UMC."
);
loadHistory();
initPanelToggle();
initTabs();
initSuggestions();
loadKnowledge();
userInput.focus();