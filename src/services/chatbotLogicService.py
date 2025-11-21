from datetime import datetime
import logging
import re
from src.services.recommenderService import recommender_service
from src.services.conversationService import conversation_service
from src.services.modelService import models_service
import pandas as pd

# Memoria temporal
conversation_state = {}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatbotLogicService:

    def __init__(self, df_final=None, X_embeddings=None):
        self.conversation_service = conversation_service
        self.df_final = df_final
        self.X_embeddings = X_embeddings

    # ======================================================
    # FUNCIÓN PRINCIPAL MEJORADA (COMPATIBLE)
    # ======================================================
    def procesar_mensaje(self, user_message, id_conversation, state=None):
        user_message = user_message.lower().strip()
        
        if not user_message:
            return self._responder(id_conversation, ["😊 ¿Podrías escribirme algo? Estoy aquí para ayudarte."])

        conv_id = self._iniciar_conversacion_si_necesario(id_conversation)
        self.conversation_service.save_message(conv_id, "user", user_message)

        if not self._modelos_disponibles():
            return self._responder(conv_id, ["⚠️ Lo siento, en este momento no tengo acceso al catálogo de cursos."])

        state = conversation_state.setdefault(
            conv_id, {"step": 1, "tema": None, "modalidad": None, "publico": None}
        )

        # ➊ DETECCIÓN MEJORADA DE NÚMEROS (más flexible)
        numero_seleccion = self._extraer_numero(user_message)
        if numero_seleccion is not None and state.get("step") in [4, 5]:
            return self._procesar_seleccion_numerica(conv_id, state, numero_seleccion)

        # ➋ RESPUESTAS MÁS FLEXIBLES PARA VER MÁS CURSOS
        if state.get("step") == 4:
            return self._procesar_respuesta_ver_mas(conv_id, state, user_message)

        # ➌ Flujo normal
        reply = self._gestionar_flujo(conv_id, state, user_message)

        if state["step"] == 4:
            reply = self._generar_recomendaciones(conv_id, state)

        return self._responder(conv_id, reply)

    # ======================================================
    # EXTRACCIÓN FLEXIBLE DE NÚMEROS
    # ======================================================
    def _extraer_numero(self, texto):
        """Extrae números de diferentes formatos: '1', 'curso 2', 'quiero el 3', etc."""
        # Buscar patrones como "curso 1", "el 2", "número 3", etc.
        patrones = [
            r'curso\s*(\d+)',
            r'el\s*(\d+)',
            r'número\s*(\d+)',
            r'opción\s*(\d+)',
            r'ver\s*el\s*(\d+)',
            r'quiero\s*el\s*(\d+)',
            r'^(\d+)$'  # Solo número
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None

    # ======================================================
    # PROCESAR RESPUESTAS PARA VER MÁS CURSOS (MÁS FLEXIBLE)
    # ======================================================
    def _procesar_respuesta_ver_mas(self, conv_id, state, user_message):
        opciones_si = ["s", "si", "sí", "y", "yes", "dale", "claro", "por supuesto", "ok", "vale", "afirmativo", "por favor"]
        opciones_no = ["n", "no", "nop", "nel", "para nada", "no gracias", "basta", "detente", "stop"]
        
        msg = user_message.lower()
        
        # Si estamos mostrando alternativas por falta de resultados filtrados
        if state.get("mostrando_alternativas"):
            if any(si in msg for si in opciones_si):
                # Usar los resultados alternativos
                state["filtrados_list"] = state.get("resultados_alternativos", [])
                state["mostrando_alternativas"] = False
                state["offset"] = 0
                return self._generar_lista_cursos_desde_alternativas(conv_id, state)
            else:
                state["mostrando_alternativas"] = False
                return self._responder(conv_id, [
                    "✅ Entendido!",
                    "¿Quieres intentar con otros filtros o buscar un tema diferente?"
                ])
        
        # Comportamiento normal para ver más cursos
        if any(si in msg for si in opciones_si):
            return self._responder(conv_id, self._generar_recomendaciones(conv_id, state))
        elif any(no in msg for no in opciones_no):
            state["step"] = 5
            return self._responder(conv_id, [
                "¡Perfecto! 😊",
                "¿Cuál de los cursos te llamó más la atención?",
                "Puedes decirme el número (como '1' o 'curso 3') o contarme qué buscas específicamente."
            ])
        else:
            return self._responder(conv_id, [
                "No estoy segura de entender... 🤔",
                "¿Te gustaría ver más cursos? Puedes decirme 'sí' para continuar o 'no' para elegir uno."
            ])

    def _generar_lista_cursos_desde_alternativas(self, conv_id, state):
        """Generar lista de cursos cuando se usan resultados alternativos"""
        filtrados_list = state.get("filtrados_list", [])
        total = len(filtrados_list)

        cs = conversation_state.setdefault(conv_id, state)
        cs.setdefault("offset", 0)

        inicio = cs["offset"]
        fin = min(inicio + 4, total)

        mensajes = [
            "✨ **Estas son las opciones disponibles (sin filtros aplicados):**",
            f"Mostrando {inicio + 1}-{fin} de {total}:"
        ]

        for i in range(inicio, fin):
            row = filtrados_list[i]
            nombre = str(row.get("NOMBRE_OFERTA", "")).title()
            modalidad = str(row.get("MODALIDAD", "")).capitalize()
            portafolio = row.get("PORTAFOLIO", "")
            
            emoji_modalidad = {
                "Virtual": "🖥️",
                "Presencial": "🏫", 
                "Mixta": "🔄"
            }
            
            if portafolio == 1:
                tipo_publico = "🎓 Bienestar"
            elif portafolio == 2:
                tipo_publico = "🌊 Extensión" 
            else:
                tipo_publico = "🔓 Varios"
            
            mensajes.append(
                f"🎓 **{i+1}. {nombre}**\n"
                f"   {emoji_modalidad.get(modalidad, '📚')} {modalidad} | {tipo_publico}"
            )

        cs["offset"] = fin

        if fin < total:
            mensajes.extend([
                "",
                f"📚 **Tengo {total - fin} cursos más**...",
                "¿Quieres ver más opciones? (sí/no)"
            ])
        else:
            cs["step"] = 5
            mensajes.extend([
                "",
                "🎯 **¿Alguno te interesa?**",
                "Puedes decirme el número del curso que quieras explorar."
            ])

        return mensajes

    # ======================================================
    # PROCESAR SELECCIÓN NUMÉRICA MEJORADA (COMPATIBLE)
    # ======================================================
    def _procesar_seleccion_numerica(self, conv_id, state, seleccion):
        if state.get("step") != 5 and state.get("step") != 4:
            return self._responder(conv_id, ["💡 Primero déjame mostrarte algunas opciones de cursos. ¡Cuéntame qué tema te interesa!"])

        filtrados = state.get("filtrados_list")
        if not filtrados:
            return self._responder(conv_id, ["😅 Parece que no tengo los cursos guardados. ¿Podríamos empezar de nuevo?"])

        if not (1 <= seleccion <= len(filtrados)):
            return self._responder(conv_id, [
                f"😕 Solo tengo {len(filtrados)} cursos disponibles.",
                "Por favor, elige un número entre 1 y " + str(len(filtrados))
            ])

        row = filtrados[seleccion - 1]

        # ID seguro
        id_raw = row.get("ID_OFERTA")
        id_oferta = int(float(id_raw)) if id_raw else None

        nombre = (
            row.get("NOMBRE_OFERTA")
            or row.get("NOMBRE_ACTIVIDAD")
            or "Curso seleccionado"
        )

        if not id_oferta:
            return self._responder(conv_id, ["⚠️ Este curso no tiene un ID válido en el sistema."])

        url = f"https://www.udea.edu.co/wps/portal/udea/web/inicio/go?goid=portafolioext&q={id_oferta}"

        # 🔥 MANTENER COMPATIBILIDAD: Enviar como array de strings
        reply = [
            "🎯 **¡Excelente elección!** Aquí tienes los detalles del curso:",
            f"**{nombre.title()}**", 
            f"🔗 Enlace al curso: {url}",
            "",
            "¿Te gustaría explorar otro curso? Solo dime el número que te interese 😊"
        ]

        return self._responder(conv_id, reply)

    # ======================================================
    # INICIAR CONVERSACIÓN MÁS NATURAL
    # ======================================================
    def _iniciar_conversacion_si_necesario(self, id_conversation):
        if id_conversation is not None:
            return int(id_conversation)

        conversation = self.conversation_service.create_conversation()
        conv_id = conversation.id_conversation

        mensajes = [
            "👋 ¡Hola! Soy tu asistente para encontrar cursos perfectos para ti.",
            "Me encanta conectar a las personas con oportunidades de aprendizaje que realmente les sirvan.",
            "Para empezar, **¿sobre qué tema te gustaría aprender?**",
            "_Puede ser cualquier cosa: programación, marketing, salud, arte, idiomas... ¡Tú dime!_ 🌟"
        ]
        for m in mensajes:
            self.conversation_service.save_message(conv_id, "bot", m)

        return conv_id

    def _modelos_disponibles(self):
        return self.df_final is not None and self.X_embeddings is not None

    # ======================================================
    # GESTIÓN DEL FLUJO MÁS NATURAL
    # ======================================================
    def _gestionar_flujo(self, conv_id, state, user_message):
        interpretacion = self._interpretar_consulta(user_message)

        if state["step"] == 1:
            state["tema"] = interpretacion["tema"] or user_message
            state["step"] = 2
            
            temas_interes = {
                "programacion": "💻 ¡La programación abre muchas puertas!",
                "salud": "🏥 El área de salud siempre está evolucionando, ¡excelente elección!",
                "marketing": "📈 El marketing digital es fundamental hoy en día.",
                "idioma": "🌍 Aprender idiomas expande tus horizontes.",
                "arte": "🎨 El arte alimenta el alma y la creatividad.",
                "agricultura": "🌱 ¡Qué maravilloso conectar con la naturaleza!",
                "liderazgo": "👥 Las habilidades de liderazgo son valiosas en cualquier área."
            }
            
            respuesta_tema = temas_interes.get(state["tema"].split()[0], "¡Interesante tema!")
            
            return [
                respuesta_tema,
                "**Para afinar la búsqueda, ¿qué modalidad prefieres?**",
                "• 🖥️ **Virtual** (desde donde estés)",
                "• 🏫 **Presencial** (en las instalaciones)", 
                "• 🔄 **Mixta** (lo mejor de ambos mundos)"
            ]

        if state["step"] == 2:
            modalidad = interpretacion["modalidad"]
            if not modalidad:
                return [
                    "🤔 No capté bien la modalidad...",
                    "¿Sería virtual, presencial o mixta? ¡La que mejor se adapte a tu ritmo! 📚"
                ]
            state["modalidad"] = modalidad
            state["step"] = 3
            
            emoji_modalidad = {
                "Virtual": "🖥️",
                "Presencial": "🏫", 
                "Mixta": "🔄"
            }
            
            return [
                f"{emoji_modalidad.get(modalidad, '✅')} **{modalidad}** - ¡Buena elección!",
                "**Última pregunta para personalizar tu búsqueda:**",
                "¿Estás buscando cursos como:",
                "• 🎓 **Estudiante interno** (de la UdeA)",
                "• 🌟 **Público externo** (cualquier persona interesada)",
                "¡Cuéntame! 👂"
            ]

        if state["step"] == 3:
            publico = interpretacion["publico"]
            if not publico:
                return [
                    "💭 ¿Sería para estudiantes de la universidad o para el público en general?",
                    "Esta info me ayuda a filtrar mejor las opciones disponibles."
                ]
            state["publico"] = publico
            state["step"] = 4
            
            return [
                "🎉 **¡Perfecto! Ya tengo toda la información.**",
                "Estoy buscando los cursos que mejor se adapten a lo que necesitas... 🔍",
                "_Dame un momentito mientras reviso el catálogo_ ⏳"
            ]

        return [
            "😅 Creo que me perdí un poco en la conversación...",
            "¿Podríamos volver a empezar? Cuéntame **¿qué te gustaría aprender?**"
        ]

    # ======================================================
    # RESPUESTA (MANTENER COMPATIBILIDAD)
    # ======================================================
    def _responder(self, conv_id, reply_list):
        if isinstance(reply_list, str):
            reply_list = [reply_list]

        for msg in reply_list:
            self.conversation_service.save_message(conv_id, "bot", msg)

        return {"reply": reply_list, "id_conversation": conv_id}

    # ======================================================
    # INTERPRETAR CONSULTA MEJORADA
    # ======================================================
    def _interpretar_consulta(self, texto):
        texto = texto.lower()
        
        # Stopwords más completas
        stopwords = ["quiero", "aprender", "sobre", "de", "en", "curso", "taller", "diplomado", "clase", "clases", "me", "gusta", "interesa"]
        palabras = [p for p in texto.split() if p not in stopwords and len(p) > 2]

        tema = " ".join(palabras) if palabras else texto

        # Detección de modalidad más flexible
        modalidad = None
        modalidad_keywords = {
            "virtual": ["virtual", "online", "internet", "remoto", "distancia"],
            "presencial": ["presencial", "fisico", "campus", "instalaciones", "personalmente"],
            "mixta": ["mixta", "hibrida", "semi", "combinada", "ambas"]
        }
        
        for mod, keywords in modalidad_keywords.items():
            if any(keyword in texto for keyword in keywords):
                modalidad = mod.capitalize()
                break

        # Detección de público más flexible
        publico = None
        if any(word in texto for word in ["externo", "general", "publico", "cualquiera", "todas", "personas"]):
            publico = "externo"
        elif any(word in texto for word in ["interno", "estudiante", "udea", "universidad", "alumno"]):
            publico = "interno"

        return {"tema": tema, "modalidad": modalidad, "publico": publico}

    # ======================================================
    # GENERAR RECOMENDACIONES MÁS ATRACTIVAS (COMPATIBLE)
    # ======================================================
    def _generar_recomendaciones(self, conv_id, state):
        # Primero obtener recomendaciones basadas en el tema
        resultados = recommender_service.obtener_recomendaciones_inteligentes_2(
            texto_usuario=state["tema"],
            df_final=self.df_final,
            X_embeddings=self.X_embeddings,
            num_recomendaciones=100  # Pedir más para tener suficiente después de filtrar
        )

        if resultados is None or resultados.empty:
            return [
                "😔 **No encontré cursos específicos** para '{}'.".format(state["tema"]),
                "Pero no te preocupes, podemos intentar:",
                "• 📝 **Buscar con otras palabras** relacionadas",
                "• 🎯 **Explorar categorías similares**", 
                "• 🔍 **Revisar todo el catálogo** disponible",
                "¿Qué te parece? ¿Quieres intentar con otro tema?"
            ]

        # 🔥 FILTRAR POR MODALIDAD Y PÚBLICO (SEGÚN LA INFORMACIÓN PROPORCIONADA)
        resultados_filtrados = resultados.copy()
        
        # 1. FILTRAR POR MODALIDAD
        if state.get("modalidad"):
            modalidad_lower = state["modalidad"].lower()
            resultados_filtrados = resultados_filtrados[
                resultados_filtrados['MODALIDAD'].fillna('').str.lower() == modalidad_lower
            ]
        
        # 2. FILTRAR POR PÚBLICO (SEGÚN PORTAFOLIO Y LÍNEA)
        if state.get("publico") == "externo":
            # Para público externo: Solo cursos de Extensión (Portafolio = 2) y Educación Continua
            condicion_portafolio = resultados_filtrados['PORTAFOLIO'].fillna(0).astype(int) == 2
            condicion_linea = resultados_filtrados['LINEA'].fillna('').str.lower().str.contains('continua|educación continua', na=False)
            
            # Aplicar filtro: debe ser de Extensión (Portafolio=2) O de Educación Continua
            resultados_filtrados = resultados_filtrados[condicion_portafolio | condicion_linea]
            
        elif state.get("publico") == "interno":
            # Para estudiantes internos: Pueden ver todos los cursos (no aplicamos filtro)
            # O si quieres mostrar solo los de Bienestar + otros relevantes:
            condicion_portafolio = resultados_filtrados['PORTAFOLIO'].fillna(0).astype(int).isin([1, 2])
            # Mantenemos todos los cursos para internos, pero podríamos priorizar algunos
            pass  # No filtramos para internos
        
        # Si después de filtrar no hay resultados, ofrecer opciones sin filtrar
        if resultados_filtrados.empty:
            # Guardar los resultados sin filtrar para ofrecer como alternativa
            state["resultados_alternativos"] = resultados.head(10).to_dict('records')
            
            mensaje_filtro = [
                f"😅 **No encontré cursos de '{state['tema']}'** que cumplan todos los filtros:",
                f"• Modalidad: {state.get('modalidad', 'Cualquiera')}",
                f"• Público: {state.get('publico', 'Cualquiera')}",
                "",
                "**Pero tengo estas opciones disponibles sin los filtros:**"
            ]
            
            # Mostrar algunas opciones alternativas
            alternativas = resultados.head(3)
            for i, (_, row) in enumerate(alternativas.iterrows(), 1):
                nombre = str(row.get("NOMBRE_OFERTA", "")).title()
                modalidad = str(row.get("MODALIDAD", "")).capitalize()
                portafolio = row.get("PORTAFOLIO", "")
                linea = row.get("LINEA", "")
                
                tipo_publico = "🔓 Ambos" if portafolio == 1 else "🌊 Externo" if portafolio == 2 else "📚 Varios"
                
                mensaje_filtro.append(f"🎓 {i}. {nombre}")
                mensaje_filtro.append(f"   📍 {modalidad} | {tipo_publico}")
            
            mensaje_filtro.extend([
                "",
                "¿Te gustaría ver estas opciones? Responde 'sí' para continuar."
            ])
            
            state["mostrando_alternativas"] = True
            return mensaje_filtro

        # Continuar con el procesamiento normal si hay resultados filtrados
        resultados_filtrados = resultados_filtrados.drop_duplicates(subset=["NOMBRE_OFERTA"])

        columnas_requeridas = [
            "ID_OFERTA", "NOMBRE_OFERTA", "MODALIDAD", "TIPO_OFERTA",
            "DESCRIPCION_GENERAL", "AREA", "UNIDAD_ADSCRITA",
            "DEPENDENCIA_PRINCIPAL", "PORTAFOLIO", "LINEA"  # 🔥 Agregar estas columnas
        ]

        for col in columnas_requeridas:
            if col not in resultados_filtrados.columns:
                resultados_filtrados[col] = None

        filtrados_list = [
            row._asdict()
            for row in resultados_filtrados[columnas_requeridas].itertuples()
        ]

        state["filtrados_list"] = filtrados_list
        total = len(filtrados_list)

        cs = conversation_state.setdefault(conv_id, state)
        cs.setdefault("offset", 0)

        inicio = cs["offset"]
        fin = min(inicio + 4, total)

        mensajes = [
            f"✨ **¡Encontré {total} cursos que se ajustan a tu búsqueda!**",
            f"Aquí tienes algunas opciones ({inicio + 1}-{fin} de {total}):"
        ]

        for i in range(inicio, fin):
            row = filtrados_list[i]
            nombre = str(row.get("NOMBRE_OFERTA", "")).title()
            modalidad = str(row.get("MODALIDAD", "")).capitalize()
            portafolio = row.get("PORTAFOLIO", "")
            linea = row.get("LINEA", "")
            
            emoji_modalidad = {
                "Virtual": "🖥️",
                "Presencial": "🏫",
                "Mixta": "🔄"
            }
            
            # Determinar el tipo de público basado en Portafolio y Línea
            if portafolio == 1:
                tipo_publico = "🎓 Bienestar (Internos)"
            elif portafolio == 2:
                tipo_publico = "🌊 Extensión (Externos)"
            elif "continua" in str(linea).lower():
                tipo_publico = "📚 Educación Continua (Externos)"
            else:
                tipo_publico = "🔓 Varios públicos"
            
            mensajes.append(
                f"🎓 **{i+1}. {nombre}**\n"
                f"   {emoji_modalidad.get(modalidad, '📚')} {modalidad} | {tipo_publico}"
            )

        cs["offset"] = fin

        if fin < total:
            mensajes.extend([
                "",
                f"📚 **Tengo {total - fin} cursos más** para mostrarte...",
                "¿Quieres que continúe con más opciones?",
                "_(Responde 'sí' para más cursos o 'no' para elegir uno)_"
            ])
        else:
            cs["step"] = 5
            mensajes.extend([
                "",
                "🎯 **¿Alguno te llamó la atención?**",
                "Puedes decirme el número (ej: '1' o 'curso 3') o contarme qué buscas específicamente."
            ])

        return mensajes

    def get_messages(self, id_conversation):
        return self.conversation_service.get_messages(id_conversation)


# Cargar modelos
df_final = models_service._models_cache["cursos"]
X_embeddings = models_service._models_cache["embeddings"]

chatbot_logic_service = ChatbotLogicService(df_final, X_embeddings)