from pathlib import Path

from nbconvert import export

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "model"
VECT_DIR = BASE_DIR / "vectorizer"

MODEL_DIR = MODEL_DIR / "modelo_clusters.pkl"
CLUSTER_MODEL_DIR = MODEL_DIR / "cluster_model.pkl"       # "kmeans_model.pkl"
RESPUESTAS_DIR = MODEL_DIR / "respuestas.json"
VECT_DIR = VECT_DIR / "vectorizer.pkl"


DB_DIR = BASE_DIR / "db"
DATABASE_DIR = DB_DIR / "db-conversaciones.db"
DATABASE_URL = f"sqlite:///{DATABASE_DIR}"

