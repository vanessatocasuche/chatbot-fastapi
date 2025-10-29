import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- importaciones del backend ---
from src.services import modelService
from src.core.database import Base, engine
from src.api.apiRouter import router as api_router


# ============================================================
# APP CONFIG
# ============================================================
app = FastAPI(title="Chatbot con Clustering y Feedback")

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Incluir rutas de la API
app.include_router(api_router)


# ============================================================
# EVENTO DE INICIO
# ============================================================
@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Iniciando sistema...")
    try:
        # Aquí podrías cargar tus modelos si lo deseas
        logging.info("--- Modelos cargados correctamente al inicio.")
    except Exception as e:
        logging.error(f"--- Error cargando modelos al inicio: {e}")


# ============================================================
# FRONTEND (Jinja2)
# ============================================================

# Configurar plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta raíz -> página HTML del chatbot
@app.get("/", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """
    Página principal del chatbot (frontend)
    """
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/models", response_class=HTMLResponse)
async def models_ui(request: Request):
    """
    Página de administración de modelos
    """
    return templates.TemplateResponse("models.html", {"request": request})


@app.get("/conversations", response_class=HTMLResponse)
async def conversations_ui(request: Request):
    """
    Página de administración de conversaciones
    """
    return templates.TemplateResponse("conversations.html", {"request": request})

@app.get("/conversations", response_class=HTMLResponse)
async def conversations_ui(request: Request):
    return templates.TemplateResponse("conversations.html", {"request": request})