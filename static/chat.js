const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// Si no hay id_conversacion en sessionStorage, se genera y guarda después del primer mensaje
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  appendMessage("user", message);
  input.value = "";
  const id_conversation_ = sessionStorage.getItem("id_conversation");
  try {
    const response = await fetch("/api/chatbot/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        id_conversation: id_conversation_ || null,
      }),
    });
    

    // Si hay un problema con la respuesta HTTP
    if (!response.ok) {
      throw new Error(`Error del servidor: ${response.status}`);
    }

    // Convertir respuesta a JSON (solo aquí)
    const data = await response.json();

    // Guardar ID de conversación si el backend lo devuelve
    if (data.id_conversation) {
      sessionStorage.setItem("id_conversation", data.id_conversation);
    }

    appendMessage("bot", data.reply);
  } catch (error) {
    appendMessage("bot", "⚠️ Hubo un problema al procesar tu mensaje.");
  }
});

// Función para agregar mensajes al chat
function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add(sender);
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Cargar historial de conversación al iniciar (si existe)
window.addEventListener("load", async () => {
  const id_conversation_ = sessionStorage.getItem("id_conversation");
  if (id_conversation_) {
    try {
      const response = await fetch(`/api/chatbot/message/${id_conversation_}`);
      const data = await response.json();
      data.messages.forEach((msg) => {
        appendMessage(msg.sender, msg.text);
      });
    } catch (error) {
      console.error("Error al cargar el historial de conversación:", error);
    }
  }
});


const resetBtn = document.getElementById("reset-chat");
resetBtn.addEventListener("click", () => {
  const confirmar = confirm("¿Seguro que deseas iniciar una nueva conversación? Se borrará el historial.");
  if (confirmar) {
    sessionStorage.removeItem("id_conversation");
    document.getElementById("chat-box").innerHTML = "";
  }
});

data.messages.forEach((msg) => {
  console.log("Mensaje del historial:", msg);
  appendMessage(msg.sender, msg.text )
});
