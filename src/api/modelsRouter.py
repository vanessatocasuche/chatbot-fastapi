# api/models_router.py
import logging
from fastapi import APIRouter, HTTPException
from src.services.modelService import models_service 

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/load")
async def load_models():
    """
    Fuerza la carga o recarga de los modelos desde la carpeta configurada.
    """
    try:
        models_service.load_models()
        logger.info("--- Modelos cargados correctamente.")
        return {"status": "ok", "message": "Modelos cargados correctamente"}
    except Exception as e:
        logger.error(f"--- Error al cargar modelos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al cargar modelos")

@router.get("/status")
async def get_model_status():
    """
    Retorna el estado actual de los modelos cargados.
    """
    status = {
        "vectorizer": models_service.embedding_model is not None,
        "cluster_model": models_service.cluster_model is not None,
        "responses": models_service.respuestas is not None,
    }
    return status
