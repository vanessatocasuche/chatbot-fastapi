from fastapi import FastAPI
from src.core.database import Base, engine


app = FastAPI(title="Chatbot con Clustering y Feedback")

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas
from src.api import check_model_status
app.include_router(check_model_status.router, prefix="/api")
