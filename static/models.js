const API_BASE = "/api/models";

const refreshStatusBtn = document.getElementById("refresh-status");
const statusDiv = document.getElementById("status-result");

const uploadForm = document.getElementById("upload-form");
const uploadResult = document.getElementById("upload-result");

const loadSelect = document.getElementById("load-type");
const loadBtn = document.getElementById("btn-load");
const loadResult = document.getElementById("load-result");

// === CONSULTAR ESTADO DE LOS MODELOS ===
async function fetchStatus() {
  statusDiv.textContent = "Consultando estado...";
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Error consultando estado");
    const data = await res.json();

    statusDiv.innerHTML = `
      <ul>
        <li>🧠 Autoencoder: <strong>${data.autoencoder ? "✅ Cargado" : "❌ No cargado"}</strong></li>
        <li>📘 Embeddings: <strong>${data.embeddings ? "✅ Cargado" : "❌ No cargado"}</strong></li>
        <li>📊 Matriz: <strong>${data.matriz ? "✅ Cargado" : "❌ No cargado"}</strong></li>
        <li>📚 Cursos: <strong>${data.cursos ? "✅ Cargado" : "❌ No cargado"}</strong></li>
        <li>📝 Cursos Info: <strong>${data.cursos_info ? "✅ Cargado" : "❌ No cargado"}</strong></li>
      </ul>
    `;
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "❌ Error al obtener el estado de los modelos.";
  }
}

// === SUBIR MODELO ===
uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const tipo = document.getElementById("model-type").value;
  const fileInput = document.getElementById("file");

  if (!tipo || !fileInput.files.length) {
    alert("Selecciona un tipo y un archivo antes de continuar.");
    return;
  }

  const formData = new FormData();
  formData.append("tipo", tipo);
  formData.append("file", fileInput.files[0]);

  uploadResult.textContent = "Subiendo archivo...";

  try {
    const res = await fetch(`${API_BASE}/`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error al subir el modelo");

    uploadResult.textContent = `✅ ${data.message || "Modelo subido correctamente."}`;
  } catch (err) {
    console.error(err);
    uploadResult.textContent = `❌ ${err.message}`;
  }
});

// === CARGAR MODELO EN MEMORIA ===
loadBtn.addEventListener("click", async () => {
  const tipo = loadSelect.value;
  if (!tipo) {
    alert("Selecciona un tipo de modelo para cargar.");
    return;
  }

  loadResult.textContent = `Cargando modelo "${tipo}"...`;

  try {
    const res = await fetch(`${API_BASE}/${tipo}/load`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error al cargar el modelo");

    loadResult.textContent = `✅ ${data.message || "Modelo cargado correctamente."}`;
  } catch (err) {
    console.error(err);
    loadResult.textContent = `❌ ${err.message}`;
  }
});

// === EVENTOS ===
refreshStatusBtn.addEventListener("click", fetchStatus);

// Cargar estado inicial
fetchStatus();
