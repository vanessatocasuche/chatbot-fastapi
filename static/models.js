const API_BASE = "/api/models";

const refreshStatusBtn = document.getElementById("refresh-status");
const statusDiv = document.getElementById("status-result");

const uploadForm = document.getElementById("upload-form");
const uploadResult = document.getElementById("upload-result");

const loadSelect = document.getElementById("load-type");
const loadBtn = document.getElementById("btn-load");
const loadResult = document.getElementById("load-result");

function renderModelStatus(tipo, isLoaded) {
  return `
    <li style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
      <span>
        ${emojiFor(tipo)} ${capitalize(tipo)}:
        <strong>${isLoaded ? "✅ Cargado" : "❌ No cargado"}</strong>
      </span>

      ${isLoaded ? `<a href="${API_BASE}/${tipo}/download" class="download-btn">⬇️ Descargar</a>` : ""}
    </li>
  `;
}

function emojiFor(tipo) {
  switch (tipo) {
    case "embeddings": return "📘";
    case "matriz": return "📊";
    case "cursos": return "📚";
    default: return "📦";
  }
}

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}


// === CONSULTAR ESTADO DE LOS MODELOS ===
async function fetchStatus() {
  statusDiv.textContent = "Consultando estado...";
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error("Error consultando estado");
    const data = await res.json();
    statusDiv.innerHTML = `
      <ul>
        ${renderModelStatus("embeddings", data.embeddings)}
        ${renderModelStatus("matriz", data.matriz)}
        ${renderModelStatus("cursos", data.cursos)}
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

// === DESCARGAR MODELO ===
loadSelect.addEventListener("change", () => {
  const tipo = loadSelect.value;
  if (tipo) {
    loadBtn.href = `${API_BASE}/${tipo}/download`;
    loadBtn.download = `${tipo}_model`;
    loadBtn.style.display = "inline-block";
  } else {
    loadBtn.style.display = "none";
  }
});

// === EVENTOS ===
refreshStatusBtn.addEventListener("click", fetchStatus);

// Cargar estado inicial
fetchStatus();
