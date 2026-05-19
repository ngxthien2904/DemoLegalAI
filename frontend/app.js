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
            addMessage(data.answer, "bot", data.sources, data.graph_relations, query);
        }
    } catch (err) {
        typingEl.remove();
        addMessage("⚠️ Không thể kết nối server. Hãy kiểm tra backend đang chạy.", "bot");
    }
    sendBtn.disabled = false;
}

function addMessage(text, role, sources, graphRelations, originalQuery) {
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
            sources.map(s => `<span class="source-tag" onclick="showDocumentDetail('${s.so_hieu}')">${s.so_hieu} - ${s.ten}</span>`).join("");
        content.appendChild(srcDiv);
    }

    if (graphRelations && graphRelations.length > 0) {
        const graphDiv = document.createElement("div");
        graphDiv.className = "graph-relations-list";
        graphDiv.innerHTML = "<small>🔗 Đồ thị kiến thức liên kết:</small><br>" +
            graphRelations.map(r => {
                const match = r.match(/(.+) \[(.+)\] (.+)/);
                if (match) {
                    const fromSohieu = match[1].trim();
                    const typeLabel = match[2].trim();
                    const toSohieu = match[3].trim();
                    return `<span class="graph-relation-tag">
                        <span class="doc-link" onclick="showDocumentDetail('${fromSohieu}')">${fromSohieu}</span>
                        <span class="relation-label">[${typeLabel}]</span>
                        <span class="doc-link" onclick="showDocumentDetail('${toSohieu}')">${toSohieu}</span>
                    </span>`;
                }
                return `<span class="graph-relation-tag">${r}</span>`;
            }).join("");
        content.appendChild(graphDiv);
    }

    // Nút xuất báo cáo Excel (chỉ cho bot, khi không có lỗi)
    if (role === "bot" && text && !text.startsWith("⚠️")) {
        const actionDiv = document.createElement("div");
        actionDiv.className = "message-actions";
        
        const exportBtn = document.createElement("button");
        exportBtn.className = "export-excel-btn";
        exportBtn.innerHTML = "📥 Xuất báo cáo Excel";
        exportBtn.dataset.query = originalQuery || "Câu hỏi pháp lý";
        exportBtn.dataset.answer = text;
        exportBtn.dataset.sources = JSON.stringify(sources || []);
        exportBtn.dataset.relations = JSON.stringify(graphRelations || []);
        
        exportBtn.onclick = function() {
            exportMessageToExcel(this);
        };
        
        actionDiv.appendChild(exportBtn);
        content.appendChild(actionDiv);
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
let network = null;
let nodesDataSet = null;
let edgesDataSet = null;
let originalNodes = [];
let originalEdges = [];
let allDocuments = []; // Sẽ lưu thông tin đầy đủ để hiển thị trên detail card

async function loadGraph() {
    if (graphLoaded) return;
    try {
        // Tải danh sách văn bản đầy đủ trước để map metadata cho card
        const docsRes = await fetch(API_BASE + "/api/documents");
        allDocuments = await docsRes.json();

        const res = await fetch(API_BASE + "/api/graph");
        const data = await res.json();

        originalNodes = data.nodes;
        originalEdges = data.edges;

        const colorMap = {
            "Luật": { background: "#6c5ce7", border: "#a29bfe", font: { color: "#fff" } },
            "Nghị định": { background: "#00b894", border: "#55efc4", font: { color: "#fff" } },
            "Thông tư": { background: "#fdcb6e", border: "#ffeaa7", font: { color: "#2d3436" } },
            "Quyết định": { background: "#e17055", border: "#fab1a0", font: { color: "#fff" } },
            "Công văn": { background: "#eff6ff", border: "#2563eb", font: { color: "#2563eb" } }
        };

        const edgeColorMap = {
            GUIDES: "#74b9ff", AMENDS: "#ff7675", REPLACES: "#d63031",
            REFERENCES: "#a29bfe", IMPLEMENTS: "#55efc4", RELATED_TO: "#636e72",
        };

        // Khởi tạo DataSet cho vis.js để có thể cập nhật động
        const rawNodes = data.nodes.map(n => ({
            id: n.id,
            label: n.label,
            title: n.title,
            color: colorMap[n.group] || { background: "#636e72" },
            shape: "box",
            borderWidth: 2,
            font: { size: 13, face: "Inter", ...(colorMap[n.group]?.font || {}) },
            margin: 12,
        }));

        const rawEdges = data.edges.map(e => ({
            from: e.from,
            to: e.to,
            label: e.label,
            arrows: "to",
            color: { color: edgeColorMap[e.type] || "#636e72", opacity: 0.85 },
            font: { size: 11, color: "#2d3436", strokeWidth: 3, strokeColor: "#ffffff", face: "Inter" },
            smooth: { type: "curvedCW", roundness: 0.2 },
        }));

        nodesDataSet = new vis.DataSet(rawNodes);
        edgesDataSet = new vis.DataSet(rawEdges);

        const container = document.getElementById("graph-network");
        network = new vis.Network(container, { nodes: nodesDataSet, edges: edgesDataSet }, {
            layout: { improvedLayout: true },
            physics: {
                solver: "forceAtlas2Based",
                forceAtlas2Based: { gravitationalConstant: -80, springLength: 200 },
                stabilization: { iterations: 150 },
            },
            interaction: { hover: true, tooltipDelay: 100 },
        });

        // ==================== SỰ KIỆN CLICK CHỌN NODE ====================
        network.on("selectNode", function (params) {
            const nodeId = params.nodes[0];
            isolateNode(nodeId);
        });

        network.on("deselectNode", function () {
            hideGraphNodeDetail();
        });

        // ==================== BỘ TÌM KIẾM ĐỒ THỊ ====================
        const searchInput = document.getElementById("graph-search-input");
        const searchBtn = document.getElementById("graph-search-btn");
        const resetBtn = document.getElementById("graph-reset-btn");

        searchInput.addEventListener("keydown", e => {
            if (e.key === "Enter") filterGraph();
        });
        searchBtn.addEventListener("click", filterGraph);
        resetBtn.addEventListener("click", resetGraphFilter);

        graphLoaded = true;
    } catch (err) {
        document.getElementById("graph-network").innerHTML =
            '<p style="padding:40px;color:#9898b8;">Không thể tải dữ liệu graph.</p>';
    }
}

// Hàm cô lập đồ thị hiển thị Node trung tâm và các Node liên quan
function filterGraph() {
    const query = document.getElementById("graph-search-input").value.trim().toLowerCase();
    if (!query) return;

    // Tìm node trùng khớp
    const targetNode = originalNodes.find(n => 
        n.label.toLowerCase().includes(query) || 
        n.title.toLowerCase().includes(query)
    );

    if (!targetNode) {
        alert("Không tìm thấy văn bản này trên đồ thị!");
        return;
    }

    isolateNode(targetNode.id);
}

function isolateNode(targetId) {
    // Tìm các edges liên quan
    const connectedEdges = originalEdges.filter(e => e.from === targetId || e.to === targetId);
    
    // Tìm tất cả các node liên quan (neighbors)
    const connectedNodeIds = new Set();
    connectedNodeIds.add(targetId);
    connectedEdges.forEach(e => {
        connectedNodeIds.add(e.from);
        connectedNodeIds.add(e.to);
    });

    // Cập nhật lại DataSet hiển thị
    const filteredNodes = originalNodes.filter(n => connectedNodeIds.has(n.id));
    const filteredEdges = originalEdges.filter(e => e.from === targetId || e.to === targetId);

    // Xóa hết và thêm lại dữ liệu đã lọc vào DataSet
    nodesDataSet.clear();
    edgesDataSet.clear();

    const colorMap = {
        "Luật": { background: "#6c5ce7", border: "#a29bfe", font: { color: "#fff" } },
        "Nghị định": { background: "#00b894", border: "#55efc4", font: { color: "#fff" } },
        "Thông tư": { background: "#fdcb6e", border: "#ffeaa7", font: { color: "#2d3436" } },
        "Quyết định": { background: "#e17055", border: "#fab1a0", font: { color: "#fff" } },
        "Công văn": { background: "#eff6ff", border: "#2563eb", font: { color: "#2563eb" } }
    };

    const edgeColorMap = {
        GUIDES: "#74b9ff", AMENDS: "#ff7675", REPLACES: "#d63031",
        REFERENCES: "#a29bfe", IMPLEMENTS: "#55efc4", RELATED_TO: "#636e72",
    };

    nodesDataSet.add(filteredNodes.map(n => ({
        id: n.id,
        label: n.label,
        title: n.title,
        color: colorMap[n.group] || { background: "#636e72" },
        shape: "box",
        borderWidth: n.id === targetId ? 4 : 2, // Viền dày hơn cho node trung tâm
        borderColor: n.id === targetId ? "#4f46e5" : null,
        shadow: n.id === targetId ? { enabled: true, color: "rgba(79,70,229,0.4)", size: 10 } : false,
        font: { size: n.id === targetId ? 15 : 13, face: "Inter", ...(colorMap[n.group]?.font || {}) },
        margin: 12,
    })));

    edgesDataSet.add(filteredEdges.map(e => ({
        from: e.from,
        to: e.to,
        label: e.label,
        arrows: "to",
        color: { color: edgeColorMap[e.type] || "#636e72", opacity: 0.95 },
        font: { size: 11, color: "#2d3436", strokeWidth: 3, strokeColor: "#ffffff", face: "Inter" },
        smooth: { type: "curvedCW", roundness: 0.2 },
    })));

    // Hiển thị nút Reset (Show All)
    document.getElementById("graph-reset-btn").classList.remove("hidden");

    // Tự động focus vào node trung tâm và chọn nó
    setTimeout(() => {
        network.focus(targetId, {
            scale: 1.2,
            animation: { duration: 800, easingFunction: "easeInOutQuad" }
        });
        network.selectNodes([targetId]);
        showGraphNodeDetail(targetId);
    }, 100);
}

function resetGraphFilter() {
    document.getElementById("graph-search-input").value = "";
    document.getElementById("graph-reset-btn").classList.add("hidden");
    hideGraphNodeDetail();

    nodesDataSet.clear();
    edgesDataSet.clear();

    const colorMap = {
        "Luật": { background: "#6c5ce7", border: "#a29bfe", font: { color: "#fff" } },
        "Nghị định": { background: "#00b894", border: "#55efc4", font: { color: "#fff" } },
        "Thông tư": { background: "#fdcb6e", border: "#ffeaa7", font: { color: "#2d3436" } },
        "Quyết định": { background: "#e17055", border: "#fab1a0", font: { color: "#fff" } },
        "Công văn": { background: "#eff6ff", border: "#2563eb", font: { color: "#2563eb" } }
    };

    const edgeColorMap = {
        GUIDES: "#74b9ff", AMENDS: "#ff7675", REPLACES: "#d63031",
        REFERENCES: "#a29bfe", IMPLEMENTS: "#55efc4", RELATED_TO: "#636e72",
    };

    nodesDataSet.add(originalNodes.map(n => ({
        id: n.id,
        label: n.label,
        title: n.title,
        color: colorMap[n.group] || { background: "#636e72" },
        shape: "box",
        borderWidth: 2,
        font: { size: 13, face: "Inter", ...(colorMap[n.group]?.font || {}) },
        margin: 12,
    })));

    edgesDataSet.add(originalEdges.map(e => ({
        from: e.from,
        to: e.to,
        label: e.label,
        arrows: "to",
        color: { color: edgeColorMap[e.type] || "#636e72", opacity: 0.85 },
        font: { size: 11, color: "#2d3436", strokeWidth: 3, strokeColor: "#ffffff", face: "Inter" },
        smooth: { type: "curvedCW", roundness: 0.2 },
    })));

    network.fit({ animation: { duration: 800 } });
}

// Hiển thị panel chi tiết văn bản ở góc dưới đồ thị
function showGraphNodeDetail(nodeId) {
    const doc = allDocuments.find(d => d.id === nodeId);
    if (!doc) return;

    const card = document.getElementById("graph-detail-card");
    const typeEl = document.getElementById("graph-card-type");
    const idEl = document.getElementById("graph-card-id");
    const titleEl = document.getElementById("graph-card-title");
    const agencyEl = document.getElementById("graph-card-agency");
    const dateEl = document.getElementById("graph-card-date");
    const statusEl = document.getElementById("graph-card-status");
    const askBtn = document.getElementById("graph-card-ask-btn");

    // Reset class cho thẻ loại
    typeEl.className = "doc-card-type";
    const typeClass = { "Luật": "luat", "Nghị định": "nghi-dinh", "Thông tư": "thong-tu", "Quyết định": "quyet-dinh", "Công văn": "cong-van" };
    typeEl.classList.add(typeClass[doc.loai] || "luat");
    typeEl.textContent = doc.loai;

    idEl.textContent = doc.so_hieu;
    titleEl.textContent = doc.ten;
    agencyEl.textContent = doc.co_quan || "Đang cập nhật";
    dateEl.textContent = doc.ngay_hieu_luc || "Đang cập nhật";
    statusEl.textContent = doc.tinh_trang || "Còn hiệu lực";

    // Gắn sự kiện click cho nút Ask AI
    askBtn.onclick = () => {
        const chatBtn = document.getElementById("nav-chat");
        if (chatBtn) chatBtn.click(); // Chuyển sang Tab Chat

        const chatInput = document.getElementById("chat-input");
        if (chatInput) {
            chatInput.value = `Tóm tắt các nội dung quan trọng nhất của văn bản ${doc.so_hieu}: ${doc.ten}`;
            chatInput.focus();
            
            // Tự động nhấn gửi sau 300ms
            setTimeout(() => {
                sendMessage();
            }, 300);
        }
    };

    card.classList.remove("hidden");
}

function hideGraphNodeDetail() {
    document.getElementById("graph-detail-card").classList.add("hidden");
}

// Gắn nút đóng detail card
document.getElementById("close-detail-btn").addEventListener("click", () => {
    network.unselectAll();
    hideGraphNodeDetail();
});

// ==================== DOCUMENTS LIST ====================
async function loadDocsList() {
    try {
        const res = await fetch(API_BASE + "/api/documents");
        const docs = await res.json();

        const list = document.getElementById("doc-list");
        list.innerHTML = docs.map(d =>
            `<div class="doc-item" data-id="${d.id}"><div class="doc-type">${d.loai}</div>${d.so_hieu}</div>`
        ).join("");

        // Thêm sự kiện click cho từng văn bản ở sidebar
        document.querySelectorAll("#doc-list .doc-item").forEach(item => {
            item.addEventListener("click", () => {
                // 1. Kích hoạt chuyển sang tab "Văn bản"
                const docsBtn = document.getElementById("nav-docs");
                if (docsBtn) docsBtn.click();
                
                // 2. Định vị card tương ứng, cuộn tới và highlight
                setTimeout(() => {
                    const cards = document.querySelectorAll(".doc-card");
                    const soHieuTarget = item.textContent.replace(item.querySelector(".doc-type").textContent, "").trim();
                    
                    cards.forEach(card => {
                        const cardIdEl = card.querySelector(".doc-card-id");
                        if (cardIdEl && cardIdEl.textContent.trim() === soHieuTarget) {
                            card.scrollIntoView({ behavior: "smooth", block: "center" });
                            card.classList.add("highlight");
                            
                            // Tự động tắt highlight sau 2 giây
                            setTimeout(() => {
                                card.classList.remove("highlight");
                            }, 2000);
                        }
                    });
                }, 200); // Đợi 200ms để tab chuyển và render hoàn tất
            });
        });

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

// Hàm hiển thị chi tiết văn bản khi click vào tag nguồn / quan hệ
function showDocumentDetail(soHieu) {
    if (!soHieu) return;

    // 1. Chuyển sang tab "Văn bản"
    const docsBtn = document.getElementById("nav-docs");
    if (docsBtn) docsBtn.click();
    
    // 2. Định vị card tương ứng, cuộn tới và highlight
    setTimeout(() => {
        const cards = document.querySelectorAll(".doc-card");
        let found = false;
        
        cards.forEach(card => {
            const cardIdEl = card.querySelector(".doc-card-id");
            if (cardIdEl && cardIdEl.textContent.trim().toLowerCase() === soHieu.trim().toLowerCase()) {
                card.scrollIntoView({ behavior: "smooth", block: "center" });
                card.classList.add("highlight");
                found = true;
                
                // Tự động tắt highlight sau 2.5 giây
                setTimeout(() => {
                    card.classList.remove("highlight");
                }, 2500);
            }
        });

        // Nếu không tìm thấy trùng khớp chính xác (ví dụ viết tắt hoặc thiếu dấu cách), thử đối sánh tương đối
        if (!found) {
            cards.forEach(card => {
                const cardIdEl = card.querySelector(".doc-card-id");
                if (cardIdEl) {
                    const idText = cardIdEl.textContent.trim().toLowerCase();
                    const cleanSoHieu = soHieu.trim().toLowerCase();
                    if (idText.includes(cleanSoHieu) || cleanSoHieu.includes(idText)) {
                        card.scrollIntoView({ behavior: "smooth", block: "center" });
                        card.classList.add("highlight");
                        
                        setTimeout(() => {
                            card.classList.remove("highlight");
                        }, 2500);
                    }
                }
            });
        }
    }, 200); // Đợi tab chuyển và render xong
}

// Hàm xuất báo cáo Excel từ dữ liệu chat
function exportMessageToExcel(btn) {
    const query = btn.dataset.query;
    const answer = btn.dataset.answer;
    const sources = JSON.parse(btn.dataset.sources || "[]");
    const relations = JSON.parse(btn.dataset.relations || "[]");

    // Hàm phụ chuyển đổi Markdown sang HTML dùng riêng trong Excel
    function formatMarkdownForExcel(text) {
        if (!text) return "";
        return text
            .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
            .replace(/\*(.*?)\*/g, "<i>$1</i>")
            .replace(/\n- /g, "\n• ")
            .replace(/\n/g, '<br style="mso-data-placement:same-cell;" />');
    }

    // Tạo nội dung HTML tương thích MS Excel
    let html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" 
                      xmlns:x="urn:schemas-microsoft-com:office:excel" 
                      xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta charset="utf-8">
<!--[if gte mso 9]><xml>
<x:ExcelWorkbook>
  <x:ExcelWorksheets>
    <x:ExcelWorksheet>
      <x:Name>Báo cáo tra cứu</x:Name>
      <x:WorksheetOptions>
        <x:DisplayGridlines/>
      </x:WorksheetOptions>
    </x:ExcelWorksheet>
  </x:ExcelWorksheets>
</x:ExcelWorkbook>
</xml><![endif]-->
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; }
  table { border-collapse: collapse; margin-bottom: 20px; table-layout: fixed; width: 850px; }
  td, th { border: 1px solid #cbd5e1; padding: 10px; text-align: left; vertical-align: top; font-size: 10pt; }
  th { background-color: #4f46e5; color: #ffffff; font-weight: bold; }
  .title-cell { background-color: #6c5ce7; color: #ffffff; font-size: 14pt; font-weight: bold; text-align: center; }
  .section-hdr { background-color: #e2e8f0; font-weight: bold; color: #0f172a; font-size: 11pt; border-bottom: 2px solid #94a3b8; }
  .meta-label { font-weight: bold; color: #475569; background-color: #f8fafc; }
  .query-text { background-color: #eff6ff; font-weight: 500; white-space: normal; mso-number-format: "\\@"; }
  .answer-text { white-space: normal; mso-number-format: "\\@"; line-height: 1.5; }
  .source-header { background-color: #2563eb; color: white; }
  .relation-header { background-color: #6c5ce7; color: white; }
</style>
</head>
<body>
  <table>
    <!-- Định nghĩa độ rộng cột để Excel tự động căn chỉnh ban đầu -->
    <colgroup>
      <col width="60" style="width: 60px;">
      <col width="150" style="width: 150px;">
      <col width="470" style="width: 470px;">
      <col width="170" style="width: 170px;">
    </colgroup>
    
    <!-- Tiêu đề báo cáo -->
    <tr>
      <td colspan="4" class="title-cell" style="height: 48px; text-align: center; vertical-align: middle;">
        BÁO CÁO KẾT QUẢ TRA CỨU PHÁP LUẬT CHỨNG KHOÁN
      </td>
    </tr>
    
    <!-- Metadata -->
    <tr>
      <td colspan="2" class="meta-label">Thời gian xuất báo cáo:</td>
      <td colspan="2" style="font-size: 10pt;">${new Date().toLocaleString('vi-VN')}</td>
    </tr>
    <tr>
      <td colspan="2" class="meta-label">Câu hỏi tra cứu:</td>
      <td colspan="2" class="query-text" style="font-size: 10pt;">
        ${query.replace(/\n/g, '<br style="mso-data-placement:same-cell;" />')}
      </td>
    </tr>
    
    <!-- Spacer -->
    <tr>
      <td colspan="4" style="border: none; height: 15px; background-color: #ffffff;"></td>
    </tr>
    
    <!-- AI Response -->
    <tr>
      <td colspan="4" class="section-hdr" style="height: 30px; vertical-align: middle; padding-left: 10px;">
        CÂU TRẢ LỜI CỦA TRỢ LÝ AI
      </td>
    </tr>`;

    // Phân tách câu trả lời thành từng dòng riêng biệt để Excel tự tính toán chiều cao hàng độc lập (tránh lỗi ẩn dòng trong Excel đối với ô gộp)
    const lines = answer.split('\n');
    lines.forEach((line, index) => {
        const trimmed = line.trim();
        if (trimmed === "") {
            // Dòng trống
            html += `
    <tr>
      <td colspan="4" style="border-left: 1px solid #cbd5e1; border-right: 1px solid #cbd5e1; border-top: none; border-bottom: none; height: 10px; background-color: #ffffff; padding: 0px;"></td>
    </tr>`;
        } else {
            // Tự động tính toán chiều cao dựa trên độ dài văn bản (khoảng 95 ký tự tiếng Việt trên 1 dòng ở font 10pt của cột rộng 850px)
            const lineCount = Math.max(1, Math.ceil(trimmed.length / 95));
            const rowHeight = lineCount * 22; // 22px cho mỗi dòng văn bản
            
            // Dòng đầu tiên của câu trả lời có đường viền trên
            const borderTopStyle = index === 0 ? "1px solid #cbd5e1" : "none";
            
            html += `
    <tr style="height: ${rowHeight}px;">
      <td colspan="4" class="answer-text" style="border-left: 1px solid #cbd5e1; border-right: 1px solid #cbd5e1; border-top: ${borderTopStyle}; border-bottom: none; padding: 6px 15px; font-size: 10pt; background-color: #ffffff; height: ${rowHeight}px; vertical-align: middle;">
        ${formatMarkdownForExcel(trimmed)}
      </td>
    </tr>`;
        }
    });

    // Đường viền đáy hộp câu trả lời AI
    html += `
    <tr>
      <td colspan="4" style="border-top: 1px solid #cbd5e1; border-bottom: none; border-left: none; border-right: none; height: 0px; padding: 0px; line-height: 0px;"></td>
    </tr>
    
    <!-- Spacer -->
    <tr>
      <td colspan="4" style="border: none; height: 15px; background-color: #ffffff;"></td>
    </tr>
    
    <!-- References Table -->
    <tr>
      <td colspan="4" class="section-hdr" style="height: 30px; vertical-align: middle; padding-left: 10px;">
        NGUỒN THAM KHẢO TRÍCH XUẤT
      </td>
    </tr>`;

    if (sources.length > 0) {
        html += `
    <tr>
      <th class="source-header" style="text-align: center; height: 26px; vertical-align: middle;">STT</th>
      <th class="source-header" style="vertical-align: middle;">Số hiệu</th>
      <th class="source-header" style="vertical-align: middle;">Tên văn bản</th>
      <th class="source-header" style="text-align: center; vertical-align: middle;">Tình trạng hiệu lực</th>
    </tr>`;
        sources.forEach((s, idx) => {
            html += `
    <tr>
      <td style="text-align: center; vertical-align: middle; border: 1px solid #cbd5e1;">${idx + 1}</td>
      <td style="white-space: normal; mso-number-format: '\\@'; border: 1px solid #cbd5e1; font-weight: bold; color: #1e3a8a;">${s.so_hieu}</td>
      <td style="white-space: normal; border: 1px solid #cbd5e1;">${s.ten}</td>
      <td style="text-align: center; vertical-align: middle; border: 1px solid #cbd5e1;">${s.tinh_trang || "Còn hiệu lực"}</td>
    </tr>`;
        });
    } else {
        html += `
    <tr>
      <td colspan="4" style="color: #64748b; font-style: italic; border: 1px solid #cbd5e1; padding: 10px;">Không có nguồn tham khảo cụ thể.</td>
    </tr>`;
    }

    // Spacer
    html += `
    <tr>
      <td colspan="4" style="border: none; height: 15px; background-color: #ffffff;"></td>
    </tr>
    
    <!-- Graph Relations -->
    <tr>
      <td colspan="4" class="section-hdr" style="height: 30px; vertical-align: middle; padding-left: 10px;">
        ĐỒ THỊ KIẾN THỨC LIÊN KẾT (KNOWLEDGE GRAPH)
      </td>
    </tr>`;

    if (relations.length > 0) {
        html += `
    <tr>
      <th class="relation-header" style="text-align: center; height: 26px; vertical-align: middle;">STT</th>
      <th class="relation-header" colspan="3" style="vertical-align: middle;">Mối liên hệ giữa các văn bản</th>
    </tr>`;
        relations.forEach((r, idx) => {
            html += `
    <tr>
      <td style="text-align: center; vertical-align: middle; border: 1px solid #cbd5e1;">${idx + 1}</td>
      <td colspan="3" style="white-space: normal; mso-number-format: '\\@'; border: 1px solid #cbd5e1; color: #5f27cd; font-weight: 500;">${r}</td>
    </tr>`;
        });
    } else {
        html += `
    <tr>
      <td colspan="4" style="color: #64748b; font-style: italic; border: 1px solid #cbd5e1; padding: 10px;">Không phát hiện mối liên hệ đồ thị bổ sung.</td>
    </tr>`;
    }

    html += `
  </table>
</body>
</html>`;

    // Download Blob
    const blob = new Blob([html], { type: "application/vnd.ms-excel;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    
    // Tạo tên file sạch
    const cleanQuery = query.substring(0, 30).replace(/[^a-zA-Z0-9 Tiếng Việt]/g, "_");
    a.download = `Bao_cao_Legal_AI_${cleanQuery}.xls`;
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
