from fastapi import HTTPException
import numpy as np
import logging
from src.services.modelService import ModelService
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import HTTPException

logger = logging.getLogger(__name__) 

# ============================================================
# SERVICE LAYER — RecommenderService
# ============================================================
class RecommenderService:
    """
    Servicio que genera recomendaciones de cursos usando:
    - Embeddings cargados desde el autoencoder.
    - Matriz de similitud.
    - Información de cursos (estructura de X_final_cursos.npy y DataFrame descriptivo).
    """

    @staticmethod
    def obtener_recomendaciones_inteligentes(
        texto_usuario,
        df_final,
        X_embeddings,
        num_recomendaciones=15,
        peso_embed=0.6,
        peso_tfidf=0.4
    ):
        # Normalizar texto de entrada
        texto_usuario = texto_usuario.lower().strip()

        # Construir corpus TF-IDF
        corpus = df_final['NOMBRE_OFERTA'].fillna('').astype(str).tolist()

        vect = TfidfVectorizer(max_features=3000)   # Limitar a 3000 características para eficiencia
        tfidf_matrix = vect.fit_transform(corpus)   # Matriz TF-IDF de los nombres de cursos
        q_vec_tfidf = vect.transform([texto_usuario])   # Vector TF-IDF del texto del usuario
        sims_tfidf = cosine_similarity(q_vec_tfidf, tfidf_matrix)[0]    # Similitud TF-IDF

        # Calcular similitud en espacio de embeddings
        top_indices = np.argsort(sims_tfidf)[::-1][:10] # Tomar top 10 para embeddings
        q_vec_embed = X_embeddings[top_indices].mean(axis=0).reshape(1, -1) # Vector promedio de embeddings
        sims_embed = cosine_similarity(q_vec_embed, X_embeddings)[0]   # Similitud en espacio de embeddings

        # Combinar similitudes con pesos ajustables
        similitud_final = peso_embed * sims_embed + peso_tfidf * sims_tfidf

        # Seleccionar top recomendaciones
        top_indices = np.argsort(similitud_final)[::-1][:num_recomendaciones * 3]   # Tomar más para filtrar duplicados
        resultados = df_final.iloc[top_indices][['NOMBRE_OFERTA', 'MODALIDAD', 'TIPO_OFERTA']]  # Seleccionar columnas relevantes
        resultados = resultados.drop_duplicates(subset='NOMBRE_OFERTA').head(num_recomendaciones)   # Filtrar duplicados y limitar al número solicitado

        return resultados

    @staticmethod
    def obtener_recomendaciones_inteligentes_2(
        texto_usuario,
        df_final,
        X_embeddings,
        num_recomendaciones=5,
        peso_embed=0.6
    ):
        # Normalizar texto de entrada
        texto_usuario = texto_usuario.lower().strip()

        # ---- Similitud semantica con TF-IDF ----
        # Construir corpus TF-IDF
        corpus_nombres = df_final['NOMBRE_OFERTA'].fillna('').astype(str).tolist()

        vect_tfidf_temp = TfidfVectorizer(max_features=3000)   # Limitar a 3000 características para eficiencia
        tfidf_temp = vect_tfidf_temp.fit_transform(corpus_nombres)   # Matriz TF-IDF de los nombres de cursos
        sims_temp = cosine_similarity(vect_tfidf_temp.transform([texto_usuario]), tfidf_temp)[0]    # Similitud de nombres

        # Calcular similitud en espacio de embeddings
        top_idx = np.argsort(sims_temp)[::-1][:10]  # Tomar top 10 índices basados en nombres
        q_vec_embed = X_embeddings[top_idx].mean(axis=0).reshape(1, -1)  # Vector promedio de embeddings de top nombres
        sims_embed = cosine_similarity(q_vec_embed, X_embeddings)[0]   # Similitud de espacio de embeddings

        # ----- Similitud textual contextual con TF-IDF ----
        corpus_contextual = (
            df_final['DESCRIPCION_GENERAL'].fillna('').astype(str) + " " +
            df_final["DEPENDENCIA_PRINCIPAL"].fillna('').astype(str)
            ).tolist()
        vect_tfidf_context = TfidfVectorizer(max_features=5000)   # Más características para contexto
        tfidf_context = vect_tfidf_context.fit_transform(corpus_contextual)   #
        sims_texto = cosine_similarity(vect_tfidf_context.transform([texto_usuario]), tfidf_context)[0]    # Similitud contextual


        # Combinar similitudes con pesos ajustables
        similitud_total = peso_embed * sims_embed + (1 - peso_embed) * sims_texto

        # Seleccionar top cursos
        top_indices = np.argsort(similitud_total)[::-1][:num_recomendaciones]   # Tomar más para filtrar duplicados
       
        columnas = ['NOMBRE_OFERTA', 'MODALIDAD', 'TIPO_OFERTA', 'DESCRIPCION_GENERAL', 'DEPENDENCIA_PRINCIPAL', 'AREA', 'UNIDAD_ADSCRITA']
        resultados = df_final.iloc[top_indices][columnas]  # Seleccionar columnas relevantes

        return resultados

    
# ============================================================
# SINGLETON INSTANCE
# ============================================================
recommender_service = RecommenderService()
