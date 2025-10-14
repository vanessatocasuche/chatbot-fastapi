from fastapi import APIRouter, HTTPException
from src.services.clusterService import cluster_service

router = APIRouter()

@router.get("/healthcheck")
def check_model_status():
    if not cluster_service.is_ready():
        raise HTTPException(status_code=503, detail="Modelos no cargados_p")
    return {"status": "ok", "message": "Modelos disponibles"}
