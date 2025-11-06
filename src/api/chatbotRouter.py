# api/chat_router.py
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from src.services.chatbotLogicService import chatbot_logic_service

logger = logging.getLogger(__name__)
router = APIRouter()

chatbot_service = chatbot_logic_service

class ChatMessage(BaseModel):
    message: str
    id_conversation: str | None = None

@router.post("/message")
def chatbot_message(msg: ChatMessage):
    response = chatbot_service.procesar_mensaje(
        user_message=msg.message,
        id_conversation=msg.id_conversation
    )
    return response