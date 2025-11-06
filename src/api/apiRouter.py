# api/api_router.py
from fastapi import APIRouter
from src.api.modelsRouter import router as models_router
from src.api.chatbotRouter import router as chatbot_router
from src.api.conversationsRouter import router as conversations_router

router = APIRouter(prefix="/api")

router.include_router(models_router, prefix="/models", tags=["Modelos"])
router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
router.include_router(conversations_router, prefix="/conversations", tags=["Conversaciones"])

# Imprimir las rutas del sistema
for route in router.routes:
    print(f"Ruta registrada: {route.path} -> {route.name}")