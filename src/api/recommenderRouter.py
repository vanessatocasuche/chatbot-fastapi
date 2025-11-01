from fastapi import APIRouter, Query
from src.services.recommenderService import RecommenderService
import logging


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def get_recommendations(q: str = Query(..., description="Texto de búsqueda del usuario")):
    """Obtiene recomendaciones de cursos basadas en el texto del usuario."""
    return RecommenderService.obtener_recomendaciones(q)
