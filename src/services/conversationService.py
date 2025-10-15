import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.conversationModel import Conversation, Message
from src.core.database import SessionLocal

logger = logging.getLogger(__name__)

class ConversationService:
    """
    Servicio encargado de:
    - Crear y mantener conversaciones
    - Guardar mensajes del usuario y del bot
    - Recuperar historial de una conversación
    """

    def __init__(self):
        # Inyectar la sesión de la base de datos
        self.session = SessionLocal()
        
    # ------------------------------------------------------------
    # MÉTODO 1: Guardar o crear la conversación
    # ------------------------------------------------------------
    def get_or_create_conversation(self, id_conversation: int | None) -> Conversation:
        """
        Retorna una conversación existente o crea una nueva si no existe.
        si no existe:
                Crea una nueva conversación en la base de datos y la guarda.
                Permite opcionalmente definir un tiempo de finalización.
                Retorna el objeto Conversation creado.

        """
        session: Session = SessionLocal()
        try:
            if id_conversation and session.query(Conversation).filter_by(id_conversation=id_conversation).first():
                return session.query(Conversation).get(id_conversation)
            else:
                new_conv = Conversation(start_time=datetime.utcnow())
                session.add(new_conv)
                session.commit()
                session.refresh(new_conv)
                logger.info(f"\n --- Nueva conversación creada con id={new_conv.id_conversation}")
                return new_conv
        except Exception as e:
            session.rollback()
            logger.error(f"\n --- Error en get_or_create_conversation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error al obtener o crear conversación")
        finally:
            session.close()

    # ------------------------------------------------------------
    # MÉTODO 2: Guardar mensaje
    # ------------------------------------------------------------
    def save_message(
        self,
        id_conversation: int | None,
        sender: str,
        content: str,
        cluster_id: int | None = None,
        confidence_score: float | None = None
    ) -> Message:
        """
        Guarda un mensaje en la base de datos.
        Si no existe la conversación, la crea.
        """
        session: Session = SessionLocal()
        try:
            # Si no hay id de conversación, crear una nueva
            if id_conversation is None:

                conversation = Conversation(start_time=datetime.utcnow())
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                id_conversation = conversation.id_conversation
                logger.info(f"\n --- Nueva conversación creada con id=     {id_conversation}")

            # Crear mensaje
            message = Message(
                id_conversation=id_conversation,
                sender=sender,
                content=content,
                cluster_id=cluster_id,
                confidence_score=confidence_score,
                created_at=datetime.utcnow()
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            logger.info(f"\n --- Mensaje guardado: sender=   {sender}, id_conversation=   {id_conversation}")
            return message

        except Exception as e:
            session.rollback()
            logger.error(f"\n --- Error al guardar mensaje: {e}", exc_info=True)
            # No interrumpimos la sesión del chatbot
            raise HTTPException(status_code=500, detail="Error al guardar el mensaje")
        finally:
            session.close()

    # ------------------------------------------------------------
    # MÉTODO 3: Recuperar historial
    # ------------------------------------------------------------
    def get_history(self, id_conversation: int) -> list[Message]:
        """
        Recupera todos los mensajes de una conversación en orden cronológico.
        """
        session: Session = SessionLocal()
        try:
            messages = (
                session.query(Message)
                .filter(Message.id_conversation == id_conversation)
                .order_by(Message.created_at.asc())
                .all()
            )
            if not messages:
                logger.warning(f"\n ---  No se encontraron mensajes para id_conversation={id_conversation}")
            return messages
        except Exception as e:
            logger.error(f"\n ---  Error al recuperar historial: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error al recuperar historial de mensajes")
    

