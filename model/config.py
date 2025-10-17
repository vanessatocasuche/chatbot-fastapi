from src.core.config import BASE_DIR

# CONFIGURACIÓN DE RUTAS 
VECT_DIR = BASE_DIR / "model" / "vectorizer"

EMBEDDING_MODEL_DIR = VECT_DIR / "pytorch_model.bin"
TOKENIZER_DIR = VECT_DIR / "tokenizer.json"
MODEL_CONFIG_DIR = VECT_DIR / "sentence-bert-config.json"
CLUSTER_MODEL_DIR = VECT_DIR / "cluster_model.pkl"
RESPUESTAS_DIR = BASE_DIR / "model" / "respuestas.json"

print("BASE_DIR:", BASE_DIR)
print("CLUSTER_MODEL_DIR:", CLUSTER_MODEL_DIR.exists())
print("RESPUESTAS_DIR:", RESPUESTAS_DIR.exists())
