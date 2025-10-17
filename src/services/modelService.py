import json
import logging
import pickle
from typing import Dict, Optional
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator
from src.core.config import RESPUESTAS_DIR
from src.core.logger import logger
from model.config import (EMBEDDING_MODEL_DIR, CLUSTER_MODEL_DIR, RESPUESTAS_DIR, TOKENIZER_DIR, MODEL_CONFIG_DIR)
import json
import numpy as np
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ============================================================
# SERVICE LAYER — ModelService
# ============================================================
class ModelService:
    """
    Servicio de gestión de modelos de IA:
    - Carga y mantiene modelos de embeddings (BERT)
    - Carga y valida modelo de clústeres (KMeans)
    - Carga respuestas asociadas a clústeres desde JSON
    """

    def __init__(self):
        self.embedding_model: Optional[SentenceTransformer] = None
        self.cluster_model: Optional[BaseEstimator] = None
        self.respuestas: Dict[int, str] = {}

    # --------------------------------------------------------
    # MÉTODO 0: Inicializar servicio
    # --------------------------------------------------------
    def initialize(self) -> bool:
        """Inicializa todos los modelos del sistema."""
        logger.info("Inicializando servicio de modelos...")
        try:
            return self.load_models()
        except Exception as e:
            logger.error(f"Fallo al inicializar ModelService: {e}", exc_info=True)
            return False

    # --------------------------------------------------------
    # MÉTODO 1: Cargar todos los modelos
    # --------------------------------------------------------
    def load_models(self) -> bool:
        """Carga el modelo de embeddings, clústeres y respuestas."""
        try:
            logger.info("Cargando modelo de embeddings...")
            self.embedding_model = self._load_embedding_model()

            logger.info("Cargando modelo de clústeres...")
            self.cluster_model = self._load_cluster_model()

            logger.info("Cargando respuestas...")
            self.respuestas = self._load_respuestas()

            logger.info("--- Todos los modelos cargados correctamente.")
            return True

        except Exception as e:
            logger.error(f"Error al cargar modelos: {e}", exc_info=True)
            self.embedding_model = None
            self.cluster_model = None
            self.respuestas.clear()
            return False

    # --------------------------------------------------------
    # MÉTODO 2: Cargar modelo de embeddings
    # --------------------------------------------------------
    def _load_embedding_model(self) -> SentenceTransformer:
        """Carga o descarga el modelo de embeddings Sentence-BERT."""
        try:
            if not EMBEDDING_MODEL_DIR.exists() or not any(EMBEDDING_MODEL_DIR.iterdir()):
                logger.warning("Modelo local no encontrado. Descargando 'all-MiniLM-L6-v2'...")
                model = SentenceTransformer("all-MiniLM-L6-v2")
                EMBEDDING_MODEL_DIR.mkdir(parents=True, exist_ok=True)
                model.save(str(EMBEDDING_MODEL_DIR))
                logger.info(f"Modelo guardado localmente en {EMBEDDING_MODEL_DIR}")
            else:
                model = SentenceTransformer(str(EMBEDDING_MODEL_DIR))
                logger.info(f"Modelo cargado desde {EMBEDDING_MODEL_DIR}")
            return model

        except Exception as e:
            logger.error(f"Error cargando modelo de embeddings: {e}", exc_info=True)
            raise

    # --------------------------------------------------------
    # MÉTODO 3: Cargar modelo de clústeres
    # --------------------------------------------------------
    def _load_cluster_model(self) -> BaseEstimator:
        """Carga o regenera el modelo de clústeres (KMeans)."""
        try:
            if not CLUSTER_MODEL_DIR.exists() or CLUSTER_MODEL_DIR.stat().st_size == 0:
                raise FileNotFoundError("Modelo de clústeres no encontrado.")
            
            with open(CLUSTER_MODEL_DIR, "rb") as f:
                model = pickle.load(f)
            
            if not hasattr(model, "predict"):
                raise ValueError("El modelo cargado no tiene método predict().")

            logger.info(f"Modelo de clústeres cargado desde {CLUSTER_MODEL_DIR}")
            return model

        except Exception as e:
            logger.error(f"Error al cargar modelo de clústeres: {e}. Intentando regenerar...")
            return self._regenerate_cluster_model()

    # --------------------------------------------------------
    # MÉTODO 4: Regenerar modelo de clústeres
    # --------------------------------------------------------
    def _regenerate_cluster_model(self) -> BaseEstimator:
        """Regenera un modelo de clústeres básico y lo guarda."""
        try:
            X = np.random.rand(100, 384)  # Simulación de embeddings
            model = KMeans(n_clusters=10, random_state=42)
            model.fit(X)

            CLUSTER_MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
            with open(CLUSTER_MODEL_DIR, "wb") as f:
                pickle.dump(model, f)

            logger.info(f"Modelo KMeans regenerado y guardado en {CLUSTER_MODEL_DIR}")
            return model

        except Exception as e:
            logger.critical(f"No se pudo regenerar el modelo de clústeres: {e}", exc_info=True)
            raise

    # --------------------------------------------------------
    # MÉTODO 5: Cargar respuestas JSON
    # --------------------------------------------------------
    def _load_respuestas(self) -> Dict[int, str]:
        """Carga el diccionario de respuestas asociadas a clústeres."""
        try:
            if not RESPUESTAS_DIR.exists():
                raise FileNotFoundError(f"No se encontró {RESPUESTAS_DIR}")
            
            with open(RESPUESTAS_DIR, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("El archivo de respuestas no tiene formato válido.")

            logger.info(f"Respuestas cargadas correctamente ({len(data)} clústeres).")
            return {int(k): v for k, v in data.items()}

        except Exception as e:
            logger.error(f"Error al cargar respuestas JSON: {e}", exc_info=True)
            raise

    # --------------------------------------------------------
    # MÉTODO 6: Estado del servicio
    # --------------------------------------------------------
    def is_ready(self) -> bool:
        """Verifica si todos los componentes están disponibles."""
        return all([
            self.embedding_model is not None,
            self.cluster_model is not None,
            bool(self.respuestas)
        ])


# ============================================================
# SINGLETON (instancia global)
# ============================================================
models_service = ModelService()
if not models_service.initialize():
    logger.error("--- No se pudieron cargar los modelos. Servicio no disponible.")
else:
    logger.info("--- Servicio de modelos inicializado correctamente.")
