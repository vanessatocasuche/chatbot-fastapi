const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  appendMessage("user", message);
  input.value = "";

  try {
    const response = await fetch("/api/chat/send_message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) throw new Error("Error del servidor");

    const data = await response.json();
    appendMessage("bot", data.response || "Sin respuesta 😕");
  } catch (err) {
    appendMessage("bot", "Error al conectar con el chatbot ❌");
  }
});

function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add(sender);
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
