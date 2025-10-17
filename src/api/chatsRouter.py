# api/chat_router.py
import logging
from fastapi import APIRouter, HTTPException
from src.schemas.chatSchema import ChatRequest, ChatResponse
from src.services.responseService import response_service  
from src.services.conversationService import ConversationService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/send_message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Envía un mensaje del usuario y retorna una respuesta generada.
    Usa ResponseService para gestionar la lógica completa.
    """
    try:
        return response_service.process_message(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"--- Error procesando mensaje: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error procesando el mensaje")

@router.post("/new_conversation")
async def new_conversation():
    """
    Crea una nueva conversación (usando ConversationService).
    """
    conv_service = ConversationService()
    conversation = conv_service.save_conversation()
    return {
        "id_conversation": conversation.id_conversation,
        "created_at": conversation.start_time.isoformat()
    }
