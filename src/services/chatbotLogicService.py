
from src.services.recommenderService import RecommenderService

# ============================================================
# SERVICE LAYER — ChatbotLogicService
# ============================================================
class ChatbotLogicService:
    """
    Servicio conversacional del chatbot.
    Gestiona el flujo de diálogo con el usuario para recomendar cursos.
    """

    @staticmethod
    def procesar_mensaje(user_message: str, contexto: dict = None):
        """
        Procesa la entrada del usuario y devuelve la respuesta del chatbot.
        """
        user_message = user_message.lower().strip()

        # Detectar intención (muy simple para este prototipo)
        if any(palabra in user_message for palabra in ["hola", "buenas", "hey"]):
            return {"reply": "👋 ¡Hola! Soy tu asistente de cursos. Cuéntame qué te gustaría aprender hoy."}

        if any(palabra in user_message for palabra in ["curso", "aprender", "quiero", "buscar", "interesado", "recomendar", "sugerir", "curso", "cursos", "aprender", "estudiar", "enseñanza", "formación",
                "capacitación", "entrenamiento", "educación", "clase", "materia",
                "tema", "taller", "programa", "especialización", "certificación",
                "seminario", "aprendizaje"]):
            resultados = RecommenderService.obtener_recomendaciones(user_message)
            if not resultados:
                return {"reply": "😔 No encontré cursos relacionados, intenta con otro tema."}

            respuesta = "✨ Basado en tu interés, te recomiendo:\n\n"
            for i, r in enumerate(resultados, 1):
                respuesta += f"{i}. {r['NOMBRE_OFERTA']} ({r['MODALIDAD']}, {r['TIPO_OFERTA']})\n"
            return {"reply": respuesta.strip()}

        return {"reply": "🤖 No estoy seguro de entenderte. ¿Podrías decirme qué tema te interesa aprender?"}
