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
    id_conversation: int | None = None
    state: dict | None = None     # <── AÑADIR ESTO

@router.post("/message")
def chatbot_message(msg: ChatMessage):
    response = chatbot_service.procesar_mensaje(
        user_message=msg.message,
        id_conversation=msg.id_conversation,
        state=msg.state    # <── PASARLO TAMBIÉN AL SERVICIO
    )
    return response


@router.get("/message/{id_conversation}")
def get_conversation_messages(id_conversation: str):
    messages = chatbot_service.conversation_service.get_messages(int(id_conversation))
    return {"messages": messages}