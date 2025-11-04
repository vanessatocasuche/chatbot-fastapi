from datetime import datetime
from src.services.recommenderService import RecommenderService
from src.services.conversationService import ConversationService, conversation_service

class ChatbotLogicService:
    """
    Servicio conversacional del chatbot.
    Gestiona el flujo de diálogo y persistencia.
    """

    def __init__(self):
        self.conversation_service = conversation_service

    def procesar_mensaje(self, user_message: str, id_conversation: str | None = None):
        user_message = user_message.lower().strip()
        # Validar que el mensaje no esté vacío
        if not user_message:
            return {"reply": "⚠️ Por favor, ingresa un mensaje válido.", "id_conversation": id_conversation}

        # Guardar mensaje del usuario
        if id_conversation:
            conversation = self.conversation_service.get_conversation(int(id_conversation))
            self.conversation_service.save_message(
                id_conversation=int(id_conversation),
                sender="user",
                content=user_message
            )
        else:
            conversation = self.conversation_service.create_conversation()
            self.conversation_service.save_message(
                id_conversation=conversation.id_conversation,
                sender="user",
                content=user_message
            )

        # 3. Generar respuesta
        if any(p in user_message for p in ["hola", "buenas", "hey"]):
            reply = "👋 ¡Hola! Soy tu asistente de cursos. Cuéntame qué te gustaría aprender hoy."

        elif any(p in user_message for p in [
            "curso", "aprender", "quiero", "buscar", "interesado", "recomendar",
            "sugerir", "cursos", "estudiar", "enseñanza", "formación", "capacitación",
            "entrenamiento", "educación", "clase", "materia", "tema", "taller",
            "programa", "especialización", "certificación", "seminario", "aprendizaje"
        ]):
            resultados = RecommenderService.obtener_recomendaciones(user_message)
            if not resultados:
                reply = "😔 No encontré cursos relacionados, intenta con otro tema."
            else:
                reply = "✨ Basado en tu interés, te recomiendo:\n\n"
                for i, r in enumerate(resultados, 1):
                    reply += f"{i}. {r['NOMBRE_OFERTA']} ({r['MODALIDAD']}, {r['TIPO_OFERTA']})\n"
        else:
            reply = "🤖 No estoy seguro de entenderte. ¿Podrías decirme qué tema te interesa aprender?"

        print(f"ConversacionID: {conversation.id_conversation}")
        # Guardar mensaje del bot
        self.conversation_service.save_message(
            id_conversation=conversation.id_conversation,
            sender="bot",
            content=reply
        )

        # 5. Devolver resultado al frontend
        return {"reply": reply, "id_conversation": conversation.id_conversation}


# ============================================================
# SINGLETON INSTANCE
chatbot_logic_service = ChatbotLogicService()
# ============================================================
