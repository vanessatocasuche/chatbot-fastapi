import json
import pickle
from pathlib import Path
from typing import Any, Dict, Optional
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator
from src.core.config import RESPUESTAS_DIR
from src.core.logger import logger
from model.config import (EMBEDDING_MODEL_DIR, CLUSTER_MODEL_DIR, RESPUESTAS_DIR, TOKENIZER_DIR, MODEL_CONFIG_DIR)
import joblib, json
import numpy as np
from sklearn.cluster import KMeans

class ClusterService:
    """
    Servicio encargado de:
    - Cargar el modelo de embeddings (Sentence-BERT)
    - Cargar el modelo de clústeres (KMeans, etc.)
    - Cargar las respuestas por clúster desde JSON
    """

    def __init__(self):
        self.embedding_model: Optional[SentenceTransformer] = None
        self.cluster_model: Optional[BaseEstimator] = None
        self.respuestas: Dict[int, str] = {}

    # ------------------------------------------------------------
    # MÉTODO 1: Inicialización general
    # ------------------------------------------------------------
    def initialize(self) -> bool:
        """
        Carga todos los modelos y respuestas.
        Devuelve True si se cargaron correctamente, False si hubo error.
        """
        try:
            logger.info("\nInicializando modelos del chatbot...\n")

            logger.info("\n------------ Cargando modelo de embeddings...")
            self.embedding_model = self._load_embedding_model()
            logger.info("\n------------ Cargando modelo de clústeres...")
            self.cluster_model = self._load_cluster_model()
            logger.info("\n------------ Cargando respuestas por clúster...")
            self.respuestas = self._load_respuestas()

            logger.info("\nModelos cargados correctamente.")
            return True

        except Exception as e:
            print(f"--- Error al inicializar los modelos: {e}")
            logger.error(f"--- Error al inicializar los modelos: {e}")
            self.embedding_model = None
            self.cluster_model = None
            self.respuestas = {}
            return False


    # ------------------------------------------------------------
    # MÉTODO 2: Cargar modelo de embeddings
    # ------------------------------------------------------------
    def _load_embedding_model(self) -> SentenceTransformer:
        """
        Carga el modelo de embeddings (Sentence-BERT).
        Si no se encuentra el modelo local, descarga el preentrenado.
        """
        try:
            if not EMBEDDING_MODEL_DIR.exists() or not any(EMBEDDING_MODEL_DIR.glob("*.bin")):
                logger.warning(f"⚠️  Modelo local no encontrado o incompleto. Descargando 'all-MiniLM-L6-v2'...")
                model = SentenceTransformer("all-MiniLM-L6-v2")
                # Guarda el modelo localmente para no volver a descargarlo
                EMBEDDING_MODEL_DIR.mkdir(parents=True, exist_ok=True)
                model.save(str(EMBEDDING_MODEL_DIR))
            else:
                logger.info(f"Cargando modelo de embeddings desde {EMBEDDING_MODEL_DIR}...")
                model = SentenceTransformer(str(EMBEDDING_MODEL_DIR))
            return model
        except Exception as e:
            logger.error(f"Error cargando modelo de embeddings: {e}")
            raise

    # ------------------------------------------------------------
    # MÉTODO 3: Cargar modelo de clústeres
    # ------------------------------------------------------------
    def _load_cluster_model(self) -> BaseEstimator:
        """
        Carga el modelo de clústeres (por ejemplo, KMeans entrenado).
        Si el archivo no existe o está corrupto, intenta regenerarlo.
        """
        try:
            if not CLUSTER_MODEL_DIR.exists() or CLUSTER_MODEL_DIR.stat().st_size == 0:
                raise FileNotFoundError(f"No se encontró el modelo de clústeres en: {CLUSTER_MODEL_DIR}")

            logger.info(f"Cargando modelo de clústeres desde {CLUSTER_MODEL_DIR}...")
            with open(CLUSTER_MODEL_DIR, "rb") as f:
                cluster_model = pickle.load(f)

            if not hasattr(cluster_model, "predict"):
                raise ValueError("El modelo de clústeres no tiene un método 'predict' válido.")
            return cluster_model

        except Exception as e:
            logger.error(f"Error al cargar el modelo de clústeres: {e}. Intentando regenerarlo...")

            # ------------------------------------------------------------
            # Regenerar el modelo si el anterior no sirve
            # ------------------------------------------------------------
            try:
                # 🧩 Simulación de embeddings (solo ejemplo)
                # 👉 Aquí deberías usar tus embeddings reales si los tienes
                X = np.random.rand(100, 384)  # 100 muestras, 384 dimensiones (BERT típico)

                model = KMeans(n_clusters=10, random_state=42)
                model.fit(X)

                with open(CLUSTER_MODEL_DIR, "wb") as f:
                    pickle.dump(model, f)

                logger.info(f"Modelo KMeans regenerado y guardado en {CLUSTER_MODEL_DIR}")
                return model

            except Exception as inner_e:
                logger.error(f"No se pudo regenerar el modelo de clústeres: {inner_e}")
                raise


    # ------------------------------------------------------------
    # MÉTODO 4: Cargar respuestas desde JSON
    # ------------------------------------------------------------
    def _load_respuestas(self) -> Dict[int, str]:
        """
        Carga el archivo JSON con las respuestas asociadas a cada clúster.
        """
        if not RESPUESTAS_DIR.exists():
            raise FileNotFoundError(f"No se encontró el archivo de respuestas en: {RESPUESTAS_DIR}")

        logger.info(f"Cargando respuestas desde {RESPUESTAS_DIR}...")
        with open(RESPUESTAS_DIR, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("El archivo de respuestas no tiene formato válido (debe ser un diccionario).")

        return {int(k): v for k, v in data.items()}

    # ------------------------------------------------------------
    # MÉTODO 5: Estado del servicio
    # ------------------------------------------------------------
    def is_ready(self) -> bool:
        """Verifica si los modelos están cargados correctamente."""
        return self.embedding_model is not None and self.cluster_model is not None and bool(self.respuestas)


# ============================================================
# Instancia global (singleton)
# ============================================================
cluster_service = ClusterService()

# Inicializar al arrancar el sistema
if not cluster_service.initialize():
    logger.error("\n----------------- No se pudieron cargar los modelos. El sistema no está listo para recibir mensajes.")
else:
    logger.info("\n----------------- Servicio de clustering inicializado correctamente.")
