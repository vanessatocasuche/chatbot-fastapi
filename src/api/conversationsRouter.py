# api/conversations_router.py
import logging
from fastapi import APIRouter, HTTPException
from src.services.conversationService import ConversationService

logger = logging.getLogger(__name__)
router = APIRouter()

conversation_service = ConversationService()

@router.get("")
async def list_conversations(limit: int = 20):
    """
    Lista las conversaciones más recientes.
    """
    try:
        conversations = conversation_service.list_conversations(limit=limit)
        return conversations
    except Exception as e:
        logger.error(f"--- Error listando conversaciones: {e}")
        raise HTTPException(status_code=500, detail="Error listando conversaciones")

@router.get("/{id_conversation}")
async def get_conversation_history(id_conversation: int):
    """
    Obtiene el historial completo de una conversación.
    """
    try:
        history = conversation_service.get_conversation_history(id_conversation)
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"--- Error recuperando historial: {e}")
        raise HTTPException(status_code=500, detail="Error recuperando historial")

@router.delete("/{id_conversation}")
async def delete_conversation(id_conversation: int):
    """
    Elimina una conversación (modo debug o limpieza).
    """
    try:
        deleted = conversation_service.delete_conversation(id_conversation)
        if not deleted:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        logger.warning(f"Conversación {id_conversation} eliminada.")
        return {"status": "deleted", "id_conversation": id_conversation}
    except Exception as e:
        logger.error(f"--- Error eliminando conversación: {e}")
        raise HTTPException(status_code=500, detail="Error eliminando conversación")
