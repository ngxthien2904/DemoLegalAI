const API_BASE = "";

// ==================== TAB NAVIGATION ====================
document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
        if (btn.dataset.tab === "graph") loadGraph();
        if (btn.dataset.tab === "docs") loadDocsGrid();
    });
});

// ==================== CHAT ====================
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const suggestedQ = document.getElementById("suggested-questions");

chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
});

function askSuggestion(btn) {
    chatInput.value = btn.textContent;
    sendMessage();
}

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Hide suggestions after first message
    suggestedQ.style.display = "none";

    // Add user message
    addMessage(query, "user");
    chatInput.value = "";
    chatInput.style.height = "auto";
    sendBtn.disabled = true;

    // Add typing indicator
    const typingEl = addTypingIndicator();

    try {
        const res = await fetch(API_BASE + "/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        const data = await res.json();
        typingEl.remove();

        if (data.error) {
            addMessage("⚠️ Lỗi: " + data.error, "bot");
        } else {
            addMessage(data.answer, "bot", data.sources);
        }
    } catch (err) {
        typingEl.remove();
        addMessage("⚠️ Không thể kết nối server. Hãy kiểm tra backend đang chạy.", "bot");
    }
    sendBtn.disabled = false;
}

function addMessage(text, role, sources) {
    const msg = document.createElement("div");
    msg.className = `message ${role === "user" ? "user-message" : "bot-message"}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "user" ? "👤" : "🤖";

    const content = document.createElement("div");
    content.className = "message-content";
    content.innerHTML = formatMarkdown(text);

    if (sources && sources.length > 0) {
        const srcDiv = document.createElement("div");
        srcDiv.className = "sources-list";
        srcDiv.innerHTML = "<small>📎 Nguồn tham khảo:</small><br>" +
            sources.map(s => `<span class="source-tag">${s.so_hieu} - ${s.ten}</span>`).join("");
        content.appendChild(srcDiv);
    }

    msg.appendChild(avatar);
    msg.appendChild(content);
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const msg = document.createElement("div");
    msg.className = "message bot-message";
    msg.innerHTML = `<div class="message-avatar">🤖</div>
        <div class="message-content"><div class="typing-indicator">
            <span></span><span></span><span></span>
        </div></div>`;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
}

function formatMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/\n- /g, "\n• ")
        .replace(/\n(\d+)\. /g, "\n$1. ")
        .replace(/\n/g, "<br>");
}

// ==================== KNOWLEDGE GRAPH ====================
let graphLoaded = false;

async function loadGraph() {
    if (graphLoaded) return;
    try {
        const res = await fetch(API_BASE + "/api/graph");
        const data = await res.json();

        const colorMap = {
            "Luật": { background: "#6c5ce7", border: "#a29bfe", font: { color: "#fff" } },
            "Nghị định": { background: "#00b894", border: "#55efc4", font: { color: "#fff" } },
            "Thông tư": { background: "#fdcb6e", border: "#ffeaa7", font: { color: "#2d3436" } },
            "Quyết định": { background: "#e17055", border: "#fab1a0", font: { color: "#fff" } },
        };

        const nodes = data.nodes.map(n => ({
            id: n.id,
            label: n.label,
            title: n.title,
            color: colorMap[n.group] || { background: "#636e72" },
            shape: "box",
            borderWidth: 2,
            font: { size: 13, face: "Inter", ...(colorMap[n.group]?.font || {}) },
            margin: 12,
        }));

        const edgeColorMap = {
            GUIDES: "#74b9ff", AMENDS: "#ff7675", REPLACES: "#d63031",
            REFERENCES: "#a29bfe", IMPLEMENTS: "#55efc4", RELATED_TO: "#636e72",
        };

        const edges = data.edges.map(e => ({
            from: e.from,
            to: e.to,
            label: e.label,
            arrows: "to",
            color: { color: edgeColorMap[e.type] || "#636e72", opacity: 0.8 },
            font: { size: 10, color: "#b2bec3", strokeWidth: 0, face: "Inter" },
            smooth: { type: "curvedCW", roundness: 0.2 },
        }));

        const container = document.getElementById("graph-network");
        new vis.Network(container, { nodes, edges }, {
            layout: { improvedLayout: true },
            physics: {
                solver: "forceAtlas2Based",
                forceAtlas2Based: { gravitationalConstant: -60, springLength: 180 },
                stabilization: { iterations: 150 },
            },
            interaction: { hover: true, tooltipDelay: 100 },
        });

        graphLoaded = true;
    } catch (err) {
        document.getElementById("graph-network").innerHTML =
            '<p style="padding:40px;color:#9898b8;">Không thể tải dữ liệu graph.</p>';
    }
}

// ==================== DOCUMENTS LIST ====================
async function loadDocsList() {
    try {
        const res = await fetch(API_BASE + "/api/documents");
        const docs = await res.json();

        const list = document.getElementById("doc-list");
        list.innerHTML = docs.map(d =>
            `<div class="doc-item"><div class="doc-type">${d.loai}</div>${d.so_hieu}</div>`
        ).join("");

        // Update status
        const badge = document.getElementById("status-badge");
        badge.innerHTML = `<span class="status-dot online"></span><span>${docs.length} văn bản</span>`;
    } catch (e) {
        document.getElementById("status-badge").innerHTML =
            `<span class="status-dot"></span><span>Offline</span>`;
    }
}

async function loadDocsGrid() {
    try {
        const res = await fetch(API_BASE + "/api/documents");
        const docs = await res.json();
        const grid = document.getElementById("docs-grid");

        const typeClass = { "Luật": "luat", "Nghị định": "nghi-dinh", "Thông tư": "thong-tu", "Quyết định": "quyet-dinh" };

        grid.innerHTML = docs.map(d => `
            <div class="doc-card">
                <div class="doc-card-header">
                    <span class="doc-card-type ${typeClass[d.loai] || ''}">${d.loai}</span>
                    <span class="doc-card-id">${d.so_hieu}</span>
                </div>
                <h3>${d.ten}</h3>
                <div class="doc-card-status ${d.tinh_trang.includes('Còn') ? 'active' : 'expired'}">
                    ${d.tinh_trang.includes('Còn') ? '🟢' : '🔴'} ${d.tinh_trang}
                </div>
            </div>
        `).join("");
    } catch (e) {
        document.getElementById("docs-grid").innerHTML =
            '<p style="color:#9898b8;">Không thể tải danh sách văn bản.</p>';
    }
}

// ==================== INIT ====================
loadDocsList();
