"""
Servicio encargado de procesar los mensajes del usuario:
- Validar entrada
- Generar embeddings
- Predecir clúster
- Calcular confidence_score
- Seleccionar la respuesta correspondiente
- Manejar errores y logs
"""

import logging
import numpy as np
from datetime import datetime
from fastapi import HTTPException
from src.schemas.chatSchema import ChatRequest, ChatResponse
from src.services.modelService import models_service
from src.services.conversationService import ConversationService  # Import ConversationService

logger = logging.getLogger(__name__)

# ============================================================
# Clase principal: ResponseService
# ============================================================
class ResponseService:
    """
    Procesa los mensajes del usuario:
    - Genera embeddings con Sentence-BERT
    - Predice clúster con modelo KMeans (u otro)
    - Devuelve la respuesta asociada
    - Guarda la conversación y mensajes en la base de datos
    """

    def __init__(self):
        self.models_service = models_service
        self.conversation_service = ConversationService()  # Inicializar ConversationService

    # ------------------------------------------------------------
    # MÉTODO 1: Procesar mensaje principal
    # ------------------------------------------------------------
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa el mensaje recibido y genera una respuesta adecuada.
        """
        #  Validar que los modelos estén listos
        if not self.models_service.is_ready():
            logger.error("\n \n--- Los modelos no están listos.")
            raise HTTPException(status_code=503, detail="Modelos no cargados correctamente.")

        #  Validar mensaje vacío
        if not request.message or not request.message.strip():
            logger.warning("\n \n--- Mensaje recibido vacío.")
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

        try:
            # --------------------------------------------------------
            # 1️. Generar embeddings
            # --------------------------------------------------------
            embedding_model = self.models_service.embedding_model
            user_embedding = embedding_model.encode([request.message])[0]  # vector de 384 dimensiones típicamente

            # --------------------------------------------------------
            # 2️. Predecir clúster
            # --------------------------------------------------------
            cluster_model = self.models_service.cluster_model
            cluster_id = int(cluster_model.predict([user_embedding])[0])

            # --------------------------------------------------------
            # 3️. Calcular confidence_score
            # --------------------------------------------------------
            # Usamos distancia inversa al centroide como "confianza"
            cluster_center = cluster_model.cluster_centers_[cluster_id]
            distance = np.linalg.norm(user_embedding - cluster_center)
            max_distance = np.max([np.linalg.norm(user_embedding - c) for c in cluster_model.cluster_centers_])
            confidence_score = max(0.0, 1.0 - (distance / max_distance))

            # --------------------------------------------------------
            # 4️. Obtener respuesta según clúster
            # --------------------------------------------------------
            respuesta = self.models_service.respuestas.get(
                cluster_id,
                "Lo siento, no tengo una respuesta específica para tu mensaje."
            )

            # --------------------------------------------------------
            # 5️. Crear objeto de respuesta
            # --------------------------------------------------------
            if isinstance(respuesta, dict):
                respuesta = respuesta.get("message") or str(respuesta)

            response = ChatResponse(
                content=respuesta,
                cluster_id=cluster_id,
                id_conversation=request.id_conversation,
                confidence_score=round(confidence_score, 4),
                created_at=datetime.utcnow()
            )

            logger.info(
                f"\n \n--- Procesado mensaje: cluster={cluster_id}, "
                f"confianza={confidence_score:.4f}, "
                f"mensaje='{request.message[:40]}...'"
            )

            # --------------------------------------------------------
            # 6. Guardar conversación y mensajes en BD
            # --------------------------------------------------------
            conversation_service = self.conversation_service

            # Paso 1: Verificar o crear conversación válida
            conversation = conversation_service.get_or_create_conversation(request.id_conversation)
            id_conversation = conversation.id_conversation

            # Paso 2: Guardar mensaje del usuario
            user_msg = conversation_service.save_message(
                id_conversation=id_conversation,
                sender="user",
                content=request.message
            )

            # Paso 3: Guardar mensaje del bot
            bot_msg = conversation_service.save_message(
                id_conversation=id_conversation,
                sender="bot",
                content=response.content,
                cluster_id=response.cluster_id,
                confidence_score=response.confidence_score
            )

            # Paso 4: Actualizar id_conversation en la respuesta
            response.id_conversation = id_conversation

            return response

        except Exception as e:
            # --------------------------------------------------------
            # 7. Manejo de errores
            # --------------------------------------------------------
            logger.error(f"\n \n--- Error al procesar mensaje: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Ocurrió un error al procesar tu mensaje. Intenta nuevamente más tarde."
            )

# ============================================================
# Instancia global (singleton)
# ============================================================
response_service = ResponseService()