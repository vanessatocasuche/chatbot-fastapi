import logging
from fastapi import FastAPI, logger
from src.services import modelService
from src.core.database import Base, engine
from src.api.apiRouter import router as api_router

app = FastAPI(title="Chatbot con Clustering y Feedback")

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Iniciando sistema...")
    try:
        logging.info("--- Modelos cargados correctamente al inicio.")
    except Exception as e:
        logging.error(f"--- Error cargando modelos al inicio: {e}")