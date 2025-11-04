from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id_conversation = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    # Relación: una conversación tiene muchos mensajes
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id_message = Column(Integer, primary_key=True, index=True)
    id_conversation = Column(Integer, ForeignKey("conversations.id_conversation", ondelete="CASCADE"))
    sender = Column(String(20), nullable=False)  # "user" o "bot"
    content = Column(Text, nullable=False)
    cluster_id = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")


# if __name__ == "__main__":
#     from src.core.database import engine
#     Base.metadata.create_all(bind=engine)
#     print("Tablas creadas correctamente en SQLite.")
    