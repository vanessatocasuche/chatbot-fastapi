import logging
from turtle import pd
from src.core.logger import logger
from src.core.config import AUTOENCODER_DIR, EMBEDDINGS_DIR, MATRIZ_DIR, CURSOS_DIR, CURSOS_INFO_DIR
import numpy as np
from fastapi import HTTPException, UploadFile
from pathlib import Path
from src.core.config import VALID_MODEL_TYPES
import tensorflow as tf
from keras.models import load_model
import pandas as pd
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ============================================================
# SERVICE LAYER — ModelService
# ============================================================
class ModelService:
    """
    Servicio para gestionar los archivos del sistema:
    - Guarda archivos enviados desde el frontend.
    - Carga archivos existentes a memoria.
    - Valida tipo y estructura.
    """

    _path_map = {
        "autoencoder": AUTOENCODER_DIR,
        "embeddings": EMBEDDINGS_DIR,
        "matriz": MATRIZ_DIR,
        "cursos": CURSOS_DIR,
        "cursos_info": CURSOS_INFO_DIR,
    }

    _models_cache = {tipo: None for tipo in VALID_MODEL_TYPES}

    # --------------------------------------------------------
    # MÉTODO 1: Guardar archivo subido
    # --------------------------------------------------------
    @classmethod
    async def handle_upload(cls, file: UploadFile, tipo: str):
        """Guarda archivo subido desde el frontend según su tipo."""
        if tipo not in VALID_MODEL_TYPES:
            raise HTTPException(status_code=400, detail=f"Tipo no válido: {tipo}")

        dest = cls._path_map[tipo]
        Path(dest).parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(dest, "wb") as f:
                f.write(await file.read())

            logger.info(f"✅ Archivo '{tipo}' guardado correctamente en {dest}")
            return {"message": f"Archivo '{tipo}' cargado correctamente.", "path": str(dest)}

        except Exception as e:
            logger.error(f"Error guardando archivo {tipo}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --------------------------------------------------------
    # MÉTODO 2: Cargar archivo en memoria
    # --------------------------------------------------------
    @classmethod
    def load(cls, tipo: str):
        """Carga el archivo indicado en memoria (Autoencoder, Embeddings, Matriz, CSV)."""
        if tipo not in VALID_MODEL_TYPES:
            raise HTTPException(status_code=400, detail=f"Tipo no válido: {tipo}")

        path = cls._path_map[tipo]
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path}")

        try:
            if tipo == "autoencoder":
                pass
                cls._models_cache["autoencoder"] = load_model(path)
            elif tipo == "embeddings":
                cls._models_cache["embeddings"] = np.load(path)
            elif tipo == "matriz":
                cls._models_cache["matriz"] = np.load(path)
            elif tipo == "cursos":
                cls._models_cache["cursos"] = np.load(path)
            elif tipo == "cursos_info":
                cls._models_cache["cursos_info"] = pd.read_csv(path)

            logger.info(f"✅ Archivo '{tipo}' cargado correctamente desde {path}")
            return {"message": f"Archivo '{tipo}' cargado correctamente."}

        except Exception as e:
            logger.error(f"Error al cargar archivo {tipo}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --------------------------------------------------------
    # MÉTODO 3: Verificar estado
    # --------------------------------------------------------
    @classmethod
    def is_ready(cls):
        """Verifica si los modelos están cargados correctamente."""
        return {tipo: cls._models_cache[tipo] is not None for tipo in VALID_MODEL_TYPES}

    @classmethod
    def initialize(cls):
        """Inicializa cargando todos los modelos necesarios."""
        try:
            for tipo in VALID_MODEL_TYPES:
                cls.load(tipo)
            return True
        except Exception as e:
            logger.error(f"Error en inicialización: {e}")
            return False
    
    @classmethod
    def download_file(cls, tipo: str):
        if tipo not in cls._path_map:
            raise HTTPException(status_code=400, detail=f"Tipo no válido: {tipo}")

        path = cls._path_map[tipo]
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path}")

        logger.info(f"✅ Archivo '{tipo}' descargado correctamente desde {path}")
        return FileResponse(
            path=path,
            filename=path.name,
            media_type="application/octet-stream"
        )
    
# ============================================================
# SINGLETON (instancia global)
# ============================================================
models_service = ModelService()
if not models_service.initialize():
    logger.error("--- No se pudieron cargar los modelos. Servicio no disponible.")
else:
    logger.info("--- Servicio de modelos inicializado correctamente.")
