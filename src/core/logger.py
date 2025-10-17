import logging

logger = logging.getLogger("models_service")
logger.setLevel(logging.INFO)

# Si no existe handler, agregar uno básico
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)