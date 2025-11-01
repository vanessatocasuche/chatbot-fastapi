# api/chat_router.py
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from src.services.chatbotLogicService import ChatbotLogicService

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.post("/message")
def chatbot_message(msg: ChatMessage):
    """Procesa un mensaje del usuario y retorna la respuesta del chatbot."""
    return ChatbotLogicService.procesar_mensaje(msg.message)