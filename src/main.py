from fastapi import FastAPI
from src.core.database import Base, engine

from src.models.chat_models import Conversation, Message, Feedback

app = FastAPI(title="Chatbot con Clustering y Feedback")

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)