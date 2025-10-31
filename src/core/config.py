from pathlib import Path

#  Configuraciones de rutas y base de datos
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Bases de datos
DB_DIR = BASE_DIR / "db"
DATABASE_DIR = DB_DIR / "db-conversaciones.db"
DATABASE_URL = f"sqlite:///{DATABASE_DIR}"

# CONFIGURACIÓN DE RUTAS 
VECT_DIR = BASE_DIR / "model" / "vectorizer"

EMBEDDING_MODEL_DIR = VECT_DIR / "pytorch_model.bin"
TOKENIZER_DIR = VECT_DIR / "tokenizer.json"
MODEL_CONFIG_DIR = VECT_DIR / "sentence-bert-config.json"
CLUSTER_MODEL_DIR = VECT_DIR / "cluster_model.pkl"
RESPUESTAS_DIR = BASE_DIR / "model" / "respuestas.json"

#  Configuraciones de archivos de modelos
FILES_DIR = BASE_DIR / "files"
VALID_MODEL_TYPES = ["autoencoder", "embeddings", "matriz", "cursos"]

AUTOENCODER_DIR = FILES_DIR / "autoencoder_model.keras"
EMBEDDINGS_DIR = FILES_DIR / "embeddings.npy"
MATRIZ_DIR = FILES_DIR / "matriz_de_similitud.npy"
CURSOS_DIR = FILES_DIR / "cursos.npy"

# import subprocess
# import getpass

# usuario = getpass.getuser()
# carpeta = "model"

# cmd = f'icacls "{carpeta}" /grant {usuario}:(F) /T'
# subprocess.run(cmd, shell=True)
# print(" Permisos ACL actualizados para el usuario:", usuario)