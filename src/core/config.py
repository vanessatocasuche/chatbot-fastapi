from pathlib import Path

#  Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Base de datos
DB_DIR = BASE_DIR / "db"
DATABASE_DIR = DB_DIR / "db-conversaciones.db"
DATABASE_URL = f"sqlite:///{DATABASE_DIR}"

#  Configuraciones de archivos de modelos
FILES_DIR = BASE_DIR / "files"
VALID_MODEL_TYPES = ["autoencoder", "embeddings", "matriz", "cursos", "cursos_info"]

AUTOENCODER_DIR = FILES_DIR / "autoencoder_model.keras"
EMBEDDINGS_DIR = FILES_DIR / "embeddings.npy"
MATRIZ_DIR = FILES_DIR / "matriz_de_similitud.npy"
CURSOS_DIR = FILES_DIR / "cursos.npy"
CURSOS_INFO_DIR = FILES_DIR / "cursos_info.csv"
