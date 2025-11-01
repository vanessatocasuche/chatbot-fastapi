# api/models_router.py
import logging
from fastapi import APIRouter, Form, UploadFile, HTTPException
from src.services.modelService import models_service 
from src.services.modelService import ModelService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def upload_model(file: UploadFile, tipo: str = Form(...)):
    """
    Sube y guarda un archivo de modelo en el servidor.

    Parámetros aceptados:
    - tipo: str — uno de ["autoencoder", "embeddings", "matriz", "cursos", "cursos_info"]
    - file: archivo correspondiente al tipo seleccionado
    """
    return await ModelService.handle_upload(file, tipo)

@router.post("/{tipo}/load")
async def load_model(tipo: str):
    """Carga un archivo en memoria según su tipo."""
    return ModelService.load(tipo)

@router.get("/status")
async def model_status():
    """Verifica qué modelos están cargados en memoria."""
    return ModelService.is_ready()




