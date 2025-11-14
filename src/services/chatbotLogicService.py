from datetime import datetime
import logging
from src.services.recommenderService import recommender_service
from src.services.conversationService import conversation_service
from src.services.modelService import models_service
import pandas as pd


# Estado de conversaciones (memoria temporal)
conversation_state = {}  

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatbotLogicService:
    """
    Servicio conversacional del chatbot.
    Gestiona el flujo de diálogo y persistencia.
    """

    def __init__(self, df_final=None, X_embeddings=None):
        self.conversation_service = conversation_service
        self.df_final = df_final
        self.X_embeddings = X_embeddings

    # ======================================================
    # FUNCIÓN PRINCIPAL
    # ======================================================
    def procesar_mensaje(self, user_message: str, id_conversation: str | None = None):
        """
        Procesa un mensaje del usuario y devuelve la respuesta del chatbot.
        """
        user_message = user_message.lower().strip()
        if not user_message:
            return {"reply": "⚠️ Por favor, ingresa un mensaje válido."}

        # 1️⃣ Iniciar conversación si no existe
        conv_id = self._iniciar_conversacion_si_necesario(id_conversation)
        self.conversation_service.save_message(conv_id, "user", user_message)

        # 2️⃣ Validar modelos cargados
        if not self._modelos_disponibles():
            reply = "⚠️ Aún no tengo cursos cargados. Pídele a un administrador que suba los modelos."
            return self._responder(conv_id, reply)
        
        # Si el mensaje es una solicitud de que le muestre más cursos
        if user_message in ["s", "sí", "si", "quiero ver más", "más cursos", "ver más"]:
            state = conversation_state.get(conv_id)
            if state and state["step"] == 4:
                reply = self._generar_recomendaciones(conv_id, state)
                return self._responder(conv_id, reply)

        # 3️⃣ Gestionar flujo conversacional
        state = conversation_state.setdefault(conv_id, {"step": 1, "tema": None, "modalidad": None, "publico": None})
        reply = self._gestionar_flujo(conv_id, state, user_message)

        # Si se completaron los 3 pasos, generar recomendaciones
        if state["step"] == 4:
            reply = self._generar_recomendaciones(conv_id, state)

        # 4️⃣ Responder al usuario
        return self._responder(conv_id, reply)

    # ======================================================
    # MÉTODOS DE APOYO
    # ======================================================
    def _iniciar_conversacion_si_necesario(self, id_conversation):
        """Crea una nueva conversación si no existe y envía mensajes de bienvenida."""
        if id_conversation is not None:
            return int(id_conversation)

        conversation = self.conversation_service.create_conversation()
        conv_id = conversation.id_conversation

        mensajes = [
            "🤖 ¡Hola! Soy tu asistente de recomendación de cursos.",
            "Puedo ayudarte a encontrar opciones que se ajusten a tus intereses.",
            "Cuéntame primero ¿En qué tema estás interesado? (Ej: salud, programación, liderazgo...)"
        ]
        for m in mensajes:
            self.conversation_service.save_message(conv_id, "bot", m)
        return conv_id

    def _modelos_disponibles(self):
        """Verifica si los modelos de cursos están cargados en memoria."""
        return self.df_final is not None and self.X_embeddings is not None

    def _gestionar_flujo(self, conv_id: int, state: dict, user_message: str) -> str:
        """
        Gestiona el flujo conversacional del chatbot.
        Interpreta errores sintácticos y sigue un flujo natural:
        1. Tema
        2. Modalidad
        3. Público
        """

        # Interpretación flexible (tema, modalidad, público)
        interpretacion = self._interpretar_consulta(user_message)

        # ───────────────────────────
        # PASO 1 → TEMA
        # ───────────────────────────
        if state["step"] == 1:
            state["tema"] = interpretacion["tema"] or user_message
            state["step"] = 2
            return "Perfecto 👍 ¿Prefieres cursos virtuales, presenciales o mixtos?"

        # ───────────────────────────
        # PASO 2 → MODALIDAD
        # ───────────────────────────
        elif state["step"] == 2:
            modalidad = interpretacion["modalidad"]

            if not modalidad:
                return "¿Te gustaría modalidad virtual, presencial o mixta?"

            state["modalidad"] = modalidad
            state["step"] = 3
            return "¿El curso es para estudiantes internos o para público externo?"

        # ───────────────────────────
        # PASO 3 → PÚBLICO
        # ───────────────────────────
        elif state["step"] == 3:
            publico = interpretacion["publico"]

            if not publico:
                return "¿Para quién sería el curso? (externos o estudiantes internos)"

            state["publico"] = publico
            state["step"] = 4
            
            # Mensaje coherente con las 3 modalidades
            modalidad_str = {
                "Virtual": "virtual",
                "Presencial": "presencial",
                "Mixta": "mixta (virtual y presencial)"
            }.get(state["modalidad"], state["modalidad"].lower())

            return (
                f"Perfecto 🙌 buscaré cursos {modalidad_str} sobre '{state['tema']}' "
                f"para público {state['publico']}."
            )
        print(f'Estado actual: {state}')  # DEBUG

    def _responder(self, conv_id: int, reply: str):
        """Guarda la respuesta del bot y la devuelve al frontend."""
        self.conversation_service.save_message(conv_id, "bot", reply)
        return {"reply": reply, "id_conversation": conv_id}
    
    def _interpretar_consulta(self, texto: str):
        texto = texto.lower()

        # Palabras que no aportan a "tema"
        stopwords = [
            "quiero", "aprender", "algo", "sobre", "de", "en", "un", "una",
            "curso", "taller", "me", "interesa", "busco"
        ]

        palabras = [p for p in texto.split() if p not in stopwords]
        tema = " ".join(palabras)

        # ────────────────────────────────
        # Modalidad (acepta errores comunes)
        # ────────────────────────────────
        modalidad = None

        if any(p in texto for p in ["virt", "virut", "virtual"]):
            modalidad = "Virtual"
        elif any(p in texto for p in ["presen", "presencial", "prencial"]):
            modalidad = "Presencial"
        elif any(p in texto for p in ["mixta", "mixto", "híbrida", "hibrida", "semi", "combinada"]):
            modalidad = "Mixta"

        # ────────────────────────────────
        # Público
        # ────────────────────────────────
        publico = None

        if any(p in texto for p in ["extern", "empres", "comunidad", "egresad"]):
            publico = "externo"
        elif any(p in texto for p in ["estudiante", "docente", "interno", "administrativo"]):
            publico = "interno"

        return {"tema": tema, "modalidad": modalidad, "publico": publico}

    def _generar_recomendaciones(self, conv_id: int, state: dict) -> str:
        """Genera recomendaciones basadas en embeddings y filtros declarados por el usuario."""

        print(
            f"Generando recomendaciones para tema: {state['tema']}, "
            f"modalidad: {state['modalidad']}, público: {state['publico']}"
        )

        # =====================================================
        # 1) Obtener recomendaciones iniciales por similitud
        # =====================================================
        resultados = recommender_service.obtener_recomendaciones_inteligentes_2(
            texto_usuario=state["tema"],
            df_final=self.df_final,
            X_embeddings=self.X_embeddings,
            num_recomendaciones=50
        )

        if resultados is None or resultados.empty:
            conversation_state.pop(conv_id, None)
            return "⚠️ No pude obtener recomendaciones iniciales. Intenta con otro tema."

        # Eliminar duplicados por curso
        resultados = resultados.drop_duplicates(subset=["NOMBRE_OFERTA"])

        # =====================================================
        # 2) Construir filtros compuestos
        # =====================================================
        filtro = pd.Series(True, index=resultados.index)

        modalidad = state["modalidad"]
        publico = state["publico"]
        tema = state["tema"]

        # ---------- Modalidad ----------
        if modalidad:
            modalidad_lower = modalidad.lower()

            if modalidad_lower == "virtual":
                filtro &= resultados["MODALIDAD"].str.contains("Virtual|Mixta", case=False, na=False)

            elif modalidad_lower == "presencial":
                filtro &= resultados["MODALIDAD"].str.contains("Presencial|Mixta", case=False, na=False)

            elif modalidad_lower == "mixta":
                filtro &= resultados["MODALIDAD"].str.contains("Mixta", case=False, na=False)

        # ---------- Público ----------
        tiene_linea = "LINEA" in resultados.columns
        tiene_porta = "PORTAFOLIO" in resultados.columns

        if publico == "interno":
            if tiene_linea or tiene_porta:
                filtro &= (
                    ((resultados["PORTAFOLIO"].isin([1, 2])) if tiene_porta else True)
                    & (~resultados["LINEA"].str.contains("educacion continua", case=False, na=False)
                    if tiene_linea else True)
                )

        elif publico == "externo":
            if tiene_linea or tiene_porta:
                filtro &= (
                    ((~resultados["PORTAFOLIO"].isin([1, 2])) if tiene_porta else True)
                    | (resultados["LINEA"].str.contains("educacion continua", case=False, na=False)
                    if tiene_linea else True)
                )

        # ---------- Tema ----------
        if tema:
            filtro &= (
                resultados["AREA"].str.contains(tema, case=False, na=False)
                | resultados["UNIDAD_ADSCRITA"].str.contains(tema, case=False, na=False)
                | resultados["NOMBRE_OFERTA"].str.contains(tema, case=False, na=False)
            )

        # =====================================================
        # 3) Aplicar filtros y preparar respuesta
        # =====================================================
        filtrados = resultados[filtro]

        if filtrados.empty:
            print("\n⚠️ No encontré coincidencias exactas con tus filtros.")
            print("Pero te dejo algunas recomendaciones similares:\n")
            filtrados = resultados.head(8)
        else:
            print("\n✨ Basado en lo que me contaste, podrían interesarte estos cursos:\n")

        # =====================================================
        # 4) Formatear la respuesta
        # =====================================================
        cursos_por_pagina = 4
        total = len(filtrados)
        inicio = 0

        respuesta = "✨ Basado en lo que me contaste, podrían interesarte estos cursos:\n\n"

        while inicio < total:
            subset = filtrados.iloc[inicio:inicio + cursos_por_pagina]
            for i, row in enumerate(subset.itertuples(), start=inicio + 1):
                nombre = str(row.NOMBRE_OFERTA).strip().title()
                modalidad_curso = str(row.MODALIDAD).strip().capitalize()
                print(f"  🎓 {i}. {nombre}  —  {modalidad_curso}")
                respuesta += f"  🎓 {i}. {nombre}  —  {modalidad_curso}\n"

            inicio += cursos_por_pagina
            if inicio < total:
                respuesta += "\n¿Quieres ver más cursos? (s/n): "
                return respuesta

        print("\n✅ ¡Espero que alguno sea justo lo que buscas!\n")

        respuesta += "\n\n¿Quieres que te explique más sobre alguno?"

        # =====================================================
        # 5) Resetear estado de conversación
        # =====================================================
        conversation_state.pop(conv_id, None)

        return respuesta

    # ======================================================
    # Recuperar mensajes de conversación
    # ======================================================
    def get_messages(self, id_conversation: int):
        return self.conversation_service.get_messages(id_conversation)



# Extraer los modelos cargados en memoria
df_final = models_service._models_cache["cursos"]
X_embeddings = models_service._models_cache["embeddings"]

# ============================================================
# SINGLETON INSTANCE
chatbot_logic_service = ChatbotLogicService(df_final, X_embeddings)
# ============================================================
