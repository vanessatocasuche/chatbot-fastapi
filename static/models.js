const btnStatus = document.getElementById("btn-status");
const btnLoad = document.getElementById("btn-load");
const statusDiv = document.getElementById("status-result");
const loadDiv = document.getElementById("load-result");

const API_BASE = "/api/models";

// Ver estado de los modelos
btnStatus.addEventListener("click", async () => {
  statusDiv.textContent = "Consultando estado...";
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Error consultando el estado");
    const data = await res.json();

    statusDiv.innerHTML = `
      <ul>
        <li>📘 Vectorizer: <strong>${data.vectorizer ? "✅ Cargado" : "❌ No cargado"}</strong></li>
        <li>📊 Cluster model: <strong>${data.cluster_model ? "✅ Cargado" : "❌ No cargado"}</strong></li>
        <li>💬 Respuestas: <strong>${data.responses ? "✅ Cargado" : "❌ No cargado"}</strong></li>
      </ul>
    `;
  } catch (error) {
    statusDiv.textContent = "❌ Error al obtener el estado de los modelos.";
  }
});

// Cargar o recargar los modelos
btnLoad.addEventListener("click", async () => {
  loadDiv.textContent = "Cargando modelos...";
  try {
    const res = await fetch(`${API_BASE}/load`, { method: "POST" });
    const data = await res.json();
    loadDiv.textContent = data.message || "Carga completada.";
  } catch (error) {
    loadDiv.textContent = "❌ Error al cargar los modelos.";
  }
});
