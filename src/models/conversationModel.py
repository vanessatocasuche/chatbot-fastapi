from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime
from src.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    cluster_id = Column(Integer, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    feedback = Column(Text, nullable=True)
    sentiment = Column(Text, nullable=True)
    topic = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)