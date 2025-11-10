from datetime import datetime
import logging
from src.services.recommenderService import recommender_service
from src.services.conversationService import conversation_service
from src.services.modelService import models_service


# Estado de conversaciones (memoria temporal)
conversation_state = {}  

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatbotLogicService:
    """
    Servicio conversacional del chatbot.
    Gestiona el flujo de diálogo y persistencia.
    """

    def __init__(self, df_final=None, X_embeddings=None):
        self.conversation_service = conversation_service
        self.df_final = df_final
        self.X_embeddings = X_embeddings

    def procesar_mensaje(self, user_message: str, id_conversation: str | None = None):
        if id_conversation is None:
            conversation = self.conversation_service.create_conversation()
            conv_id = conversation.id_conversation

            # Mensajes de bienvenida
            welcome_messages = [
                "🤖 ¡Hola! Soy tu asistente de recomendación de cursos.",
                "Puedo ayudarte a encontrar opciones que se ajusten a tus intereses.",
                "Cuéntame primero ¿En qué tema estás interesado? (Ej: salud, programación, liderazgo...)"
            ]

            # Guardar y devolver el último mensaje como respuesta inicial
            for msg in welcome_messages[:-1]:
                self.conversation_service.save_message(conv_id, "bot", msg)

            reply = welcome_messages[-1]
            self.conversation_service.save_message(conv_id, "bot", reply)

            return {"reply": reply, "id_conversation": conv_id}

        # Validar que los modelos estén cargados
        if self.df_final is None or self.X_embeddings is None:
            reply = "⚠️ Aún no tengo cursos cargados. Pídele a un administrador que suba los modelos."
            self.conversation_service.save_message(conv_id, "bot", reply)
            return {"reply": reply, "id_conversation": conv_id}
        
        # Validar que el mensaje no esté vacío
        user_message = user_message.lower().strip()
        if not user_message:
            return {"reply": "⚠️ Por favor, ingresa un mensaje válido.", "id_conversation": id_conversation}

        # Recuperar o crear conversación
        if id_conversation:
            conversation = self.conversation_service.get_conversation(int(id_conversation))
        else:
            conversation = self.conversation_service.create_conversation()

        conv_id = conversation.id_conversation

        # Guardar mensaje del usuario
        self.conversation_service.save_message(conv_id, "user", user_message)

         # Estado conversacional
        if conv_id not in conversation_state:
            conversation_state[conv_id] = {"step": 1, "tema": None, "modalidad": None, "duracion": None}

        state = conversation_state[conv_id]


        # ======================
        # PASO 1 → Tema
        # ======================
        if state["step"] == 1:
            state["tema"] = user_message
            state["step"] = 2
            reply = "Perfecto 👍 ¿Prefieres cursos virtuales o presenciales?"

        # ======================
        # PASO 2 → Modalidad
        # ======================
        elif state["step"] == 2:
            if "virt" in user_message:
                state["modalidad"] = "Virtual"
            else:
                state["modalidad"] = "Presencial"
            state["step"] = 3
            reply = "¿Buscas algo corto o un programa/diplomado más completo?"

        # ======================
        # PASO 3 → Duración
        # ======================
        elif state["step"] == 3:
            if "corto" in user_message:
                state["duracion"] = "Corto"
            else:
                state["duracion"] = "Programa"

            # Ahora sí recomendar
            resultados = recommender_service.obtener_recomendaciones_inteligentes(
                texto_usuario=state["tema"],
                df_final=self.df_final,
                X_embeddings=self.X_embeddings,
                num_recomendaciones=6
            )

            # Filtrar por modalidad y duración
            filtro = (
                self.df_final['MODALIDAD'].str.contains(state["modalidad"], case=False, na=False)
                & self.df_final['TIPO_OFERTA'].str.contains(state["duracion"], case=False, na=False)
            )

            filtrados = resultados[resultados['NOMBRE_OFERTA'].isin(self.df_final[filtro]['NOMBRE_OFERTA'])]

            if filtrados.empty:
                filtrados = resultados

            reply = "✨ Basado en lo que me contaste, podrían interesarte:\n\n"
            for i, row in enumerate(filtrados.itertuples(), 1):
                reply += f"{i}. {row.NOMBRE_OFERTA} ({row.MODALIDAD}, {row.TIPO_OFERTA})\n"

            reply += "\n¿Quieres que te explique más sobre alguno?"

            # Resetear flujo
            conversation_state.pop(conv_id, None)

        # Guardar respuesta del bot
        self.conversation_service.save_message(conv_id, "bot", reply)

        # Devolver resultado al frontend
        return {"reply": reply, "id_conversation": conv_id}
    
    def get_messages(self, id_conversation: int):
        return self.conversation_service.get_messages(id_conversation)
    
        


# Extraer los modelos cargados en memoria
df_final = models_service._models_cache["cursos_info"]
X_embeddings = models_service._models_cache["embeddings"]

# ============================================================
# SINGLETON INSTANCE
chatbot_logic_service = ChatbotLogicService(df_final, X_embeddings)
# ============================================================
