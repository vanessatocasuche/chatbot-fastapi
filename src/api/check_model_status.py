from fastapi import APIRouter, HTTPException
from src.services.clusterService import cluster_service
from src.schemas.chatSchema import ChatRequest, ChatResponse
from src.services.responseService import response_service

router = APIRouter()

@router.get("/model_status")
def check_model_status():
    if not cluster_service.is_ready():
        raise HTTPException(status_code=503, detail="Modelos no cargados_p")
    return {"status": "ok", "message": "Modelos disponibles"}


@router.post("/send_message", response_model=ChatResponse)
def send_message(request: ChatRequest):
    return response_service.process_message(request)

