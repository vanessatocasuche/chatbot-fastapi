# api/models_router.py
import logging
from fastapi import APIRouter, Form, UploadFile, HTTPException
from src.services.modelService import ModelService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def upload_model(file: UploadFile, tipo: str = Form(...)):
    """
    Sube un archivo de modelo y también lo carga inmediatamente en memoria.
    """

    # 1️⃣ Guardar archivo subido
    upload_result = await ModelService.handle_upload(file, tipo)

    # 2️⃣ Intentar cargarlo a memoria inmediatamente
    try:
        load_result = ModelService.load(tipo)
    except Exception as e:
        logger.error(f"❌ El archivo se subió pero NO se pudo cargar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Archivo subido pero no se pudo cargar en memoria: {str(e)}"
        )

    return {
        "message": f"Archivo '{tipo}' SUBIDO y CARGADO correctamente.",
        "upload": upload_result,
        "load": load_result
    }


@router.post("/{tipo}/load")
async def load_model(tipo: str):
    """Carga un archivo ya existente en memoria."""
    return ModelService.load(tipo)


@router.get("/status")
async def model_status():
    """Verifica qué modelos están cargados en memoria."""
    return ModelService.is_ready()


@router.get("/{tipo}/download")
def download_model(tipo: str):
    """Descarga el archivo almacenado en el servidor."""
    return ModelService.download_file(tipo)
