from src.core.config import BASE_DIR

# CONFIGURACIÓN DE RUTAS 
VECT_DIR = BASE_DIR / "model" / "vectorizer"
DATA_DIR = BASE_DIR / "data"


EMBEDDING_MODEL_DIR = VECT_DIR / "pytorch_model.bin"
TOKENIZER_DIR = VECT_DIR / "tokenizer.json"
MODEL_CONFIG_DIR = VECT_DIR / "sentence-bert-config.json"
CLUSTER_MODEL_DIR = VECT_DIR / "cluster_model.pkl"
RESPUESTAS_DIR = BASE_DIR / "model" / "respuestas.json"
AUTOENCODER_DIR = BASE_DIR / "model" / "autoencoder_model.pth"
EMBEDDINGS_DIR = DATA_DIR / "embeddings.npy"
MATRIZ_DIR = DATA_DIR / "matriz_de_similitud.npy"
CURSOS_DIR = DATA_DIR / "cursos.csv"

print("BASE_DIR:", BASE_DIR)
print("CLUSTER_MODEL_DIR:", CLUSTER_MODEL_DIR.exists())
print("RESPUESTAS_DIR:", RESPUESTAS_DIR.exists())
