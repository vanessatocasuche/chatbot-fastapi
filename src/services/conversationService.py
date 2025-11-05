import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.conversationModel import Conversation, Message
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

class ConversationService:
    """Servicio de gestión de conversaciones y mensajes."""

    def __init__(self):
        self.model = Conversation


    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Proporciona una sesión de base de datos."""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    # ------------------------------------------------------------
    # Crear o recuperar una conversación
    # ------------------------------------------------------------
    def get_or_create_conversation(self, id_conversation: int | None) -> Conversation:
        """Retorna una conversación existente o crea una nueva si no existe."""
        with SessionLocal() as db:
            if id_conversation:
                conversation = db.query(Conversation).filter_by(id_conversation=id_conversation).first()
                if conversation:
                    return conversation
                logger.warning(f"Conversación {id_conversation} no encontrada. Creando nueva...")
            # Crear nueva conversación
            new_conv = Conversation(start_time=datetime.utcnow())
            db.add(new_conv)
            db.commit()
            db.refresh(new_conv)
            logger.info(f"Nueva conversación creada con id={new_conv.id_conversation}")
            return new_conv
    # ------------------------------------------------------------
    # Crear una conversación
    # ------------------------------------------------------------
    def create_conversation(self ) -> Conversation:
        """Crea una nueva conversación."""
        with SessionLocal() as db:
            new_conv = Conversation(start_time=datetime.utcnow())
            db.add(new_conv)
            db.commit()
            db.refresh(new_conv)
            logger.info(f"Nueva conversación creada con id={new_conv.id_conversation}")
            return new_conv
        
    # ------------------------------------------------------------
    # Traer una conversación ()GET
    # ------------------------------------------------------------
    def get_conversation(self, id_conversation: int) -> Conversation | None:
        """Trae una conversación existente por su ID."""
        with SessionLocal() as db:
            conversation = db.query(Conversation).filter_by(id_conversation=id_conversation).first()
            if conversation:
                return conversation
            logger.warning(f"Conversación {id_conversation} no encontrada.")
            return None
    
    # ------------------------------------------------------------
    # Guardar un mensaje
    # ------------------------------------------------------------
    def save_message(
        self,
        id_conversation: int | None,
        sender: str,
        content: str,
        cluster_id: int | None = None,
        confidence_score: float | None = None
    ) -> Message:
        """Guarda un mensaje en la base de datos (crea conversación si no existe)."""
        with SessionLocal() as db:
            if id_conversation is None:
                conversation = Conversation(start_time=datetime.utcnow())
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                id_conversation = conversation.id_conversation
                logger.info(f"Nueva conversación creada con id={id_conversation}")
            else:
                conversation = db.query(Conversation).filter_by(id_conversation=id_conversation).first()
                if not conversation:
                    # Si no existe (por algún error), crearla igual
                    conversation = Conversation(id_conversation=id_conversation, start_time=datetime.utcnow())
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                    logger.warning(f"Conversación {id_conversation} no existía, creada nuevamente.")

            message = Message(
                id_conversation=id_conversation,
                sender=sender,
                content=content,
                cluster_id=cluster_id,
                confidence_score=confidence_score,
                created_at=datetime.utcnow()
            )
            db.add(message)
            if sender == "user":
                conversation.end_time = datetime.utcnow()
            db.commit()
            db.refresh(message)
            logger.info(f"Mensaje guardado → id_conv={id_conversation}, sender={sender}")
            return message

    # ------------------------------------------------------------
    # Recuperar historial
    # ------------------------------------------------------------
    def get_conversation_history(self, id_conversation: int) -> list[dict]:
        """Recupera los mensajes de una conversación en orden cronológico."""
        with SessionLocal() as db:
            messages = (
                db.query(Message)
                .filter(Message.id_conversation == id_conversation)
                .order_by(Message.created_at.asc())
                .all()
            )
            if not messages:
                logger.warning(f"No se encontraron mensajes para la conversación {id_conversation}")
            return [
                {"sender": m.sender, "content": m.content, "created_at": m.created_at}
                for m in messages
            ]

    # ------------------------------------------------------------
    # Listar conversaciones
    # ------------------------------------------------------------
    def list_conversations(self, limit: int = 20) -> list[Conversation]:
        """Lista las conversaciones más recientes."""
        with SessionLocal() as db:
            return (
                db.query(Conversation)
                .order_by(Conversation.start_time.desc())
                .limit(limit)
                .all()
            )

    # ------------------------------------------------------------
    # Eliminar conversación
    # ------------------------------------------------------------
    def delete_conversation(self, id_conversation: int) -> dict:
        """Elimina una conversación y sus mensajes."""
        with SessionLocal() as db:
            convo = db.query(Conversation).filter_by(id_conversation=id_conversation).first()
            if not convo:
                logger.warning(f"Intento de eliminar conversación inexistente: {id_conversation}")
                return {"status": "error", "message": "Conversación no encontrada"}

            db.delete(convo)
            db.commit()
            logger.info(f"Conversación {id_conversation} eliminada correctamente")
            return {"status": "ok", "message": f"Conversación {id_conversation} eliminada"}
    

    # ============================================================
    # Actualiza la hora de la última actividad de la conversación
    # ============================================================
    def update_last_activity(self, id_conversation: int) -> None:
        """Actualiza la hora de la última actividad de la conversación."""
        with SessionLocal() as db:
            conversation = db.query(Conversation).filter_by(id_conversation=id_conversation).first()
            if conversation:
                conversation.last_activity = datetime.utcnow()
                db.commit()
                logger.info(f"Última actividad de la conversación {id_conversation} actualizada.")
            else:
                logger.warning(f"Conversación {id_conversation} no encontrada para actualizar última actividad.")

        
# ============================================================
# SINGLETON INSTANCE
conversation_service = ConversationService()
# ============================================================