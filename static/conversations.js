// Ajusta este BASE_URL según el router en FastAPI
// Si lo incluiste como: router.include_router(conversations_router, prefix="/api/conversations", tags=["Conversaciones"])
const BASE_URL = "/api/conversations"; 

const listContainer = document.getElementById("conversations-list");
const historySection = document.getElementById("history-section");
const historyContent = document.getElementById("history-content");
const reloadBtn = document.getElementById("reload-btn");
const closeHistoryBtn = document.getElementById("close-history");

// ====== CARGAR LISTA DE CONVERSACIONES ======
async function loadConversations() {
  try {
    const res = await fetch(`${BASE_URL}?limit=20`);
    if (!res.ok) throw new Error("Error al cargar conversaciones");

    const conversations = await res.json();
    if (!conversations || conversations.length === 0) {
      listContainer.innerHTML = "<p>No hay conversaciones registradas.</p>";
      return;
    }

    listContainer.innerHTML = "";

    conversations.forEach(conv => {
      const card = document.createElement("div");
      card.className = "conversation-card";
      card.innerHTML = `
        <div>
          <strong>ID:</strong> ${conv.id_conversation || conv.id} <br>
          <small>Último mensaje: ${conv.last_message || "N/A"}</small>
        </div>
        <div>
          <button class="action-btn btn-view" data-id="${conv.id_conversation || conv.id}">Ver</button>
          <button class="action-btn btn-delete" data-id="${conv.id_conversation || conv.id}">Eliminar</button>
        </div>
      `;
      listContainer.appendChild(card);
    });

    // Asignar eventos a botones dinámicos
    document.querySelectorAll(".btn-view").forEach(btn => {
      btn.addEventListener("click", () => viewConversation(btn.dataset.id));
    });
    document.querySelectorAll(".btn-delete").forEach(btn => {
      btn.addEventListener("click", () => deleteConversation(btn.dataset.id));
    });

  } catch (err) {
    console.error("❌ Error:", err);
    listContainer.innerHTML = `<p style="color:red;">❌ ${err.message}</p>`;
  }
}

// ====== VER HISTORIAL ======
async function viewConversation(id) {
  try {
    const res = await fetch(`${BASE_URL}/${id}`);
    if (!res.ok) throw new Error("Error al obtener historial");

    const history = await res.json();

    // Mostrar el historial de forma legible
    historyContent.innerHTML = `
      <h3>Historial de conversación ${id}</h3>
      <pre>${JSON.stringify(history, null, 2)}</pre>
    `;
    historySection.hidden = false;

    window.scrollTo({ top: historySection.offsetTop, behavior: "smooth" });
  } catch (err) {
    console.error("❌ Error:", err);
    alert("❌ No se pudo obtener el historial de la conversación.");
  }
}

// ====== ELIMINAR CONVERSACIÓN ======
async function deleteConversation(id) {
  if (!confirm(`¿Eliminar conversación ${id}?`)) return;

  try {
    const res = await fetch(`${BASE_URL}/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Error al eliminar conversación");

    alert("✅ Conversación eliminada correctamente");
    loadConversations();
  } catch (err) {
    console.error("❌ Error:", err);
    alert("❌ No se pudo eliminar la conversación.");
  }
}

// ====== EVENTOS ======
if (reloadBtn) reloadBtn.addEventListener("click", loadConversations);
if (closeHistoryBtn) closeHistoryBtn.addEventListener("click", () => {
  historySection.hidden = true;
});

// ====== INICIAL ======
document.addEventListener("DOMContentLoaded", loadConversations);
