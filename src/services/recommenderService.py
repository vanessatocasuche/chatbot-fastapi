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
        num_recomendaciones=5,
        peso_embed=0.6,
        peso_tfidf=0.4
    ):
        texto_usuario = texto_usuario.lower().strip()

        corpus = df_final['NOMBRE_OFERTA'].fillna('').astype(str).tolist()

        vect = TfidfVectorizer(max_features=5000)
        tfidf_matrix = vect.fit_transform(corpus)
        q_vec_tfidf = vect.transform([texto_usuario])
        sims_tfidf = cosine_similarity(q_vec_tfidf, tfidf_matrix)[0]

        top_indices = np.argsort(sims_tfidf)[::-1][:10]
        q_vec_embed = X_embeddings[top_indices].mean(axis=0).reshape(1, -1)
        sims_embed = cosine_similarity(q_vec_embed, X_embeddings)[0]

        similitud_final = peso_embed * sims_embed + peso_tfidf * sims_tfidf

        top_indices = np.argsort(similitud_final)[::-1][:num_recomendaciones * 3]
        resultados = df_final.iloc[top_indices][['NOMBRE_OFERTA', 'MODALIDAD', 'TIPO_OFERTA']]
        resultados = resultados.drop_duplicates(subset='NOMBRE_OFERTA').head(num_recomendaciones)

        return resultados

    @staticmethod
    def obtener_recomendaciones(query: str, num_recomendaciones: int = 5):
        """
        Retorna cursos recomendados según el texto del usuario (query).
        Combina similitud TF-IDF + similitud de embeddings.
        """

        modelos = ModelService._models_cache

        # --------------------------------------------------------
        # 1. Verificar que los modelos estén cargados
        # --------------------------------------------------------
        for key in ["embeddings", "matriz", "cursos"]:
            if modelos.get(key) is None:
                raise HTTPException(status_code=400, detail=f"❌ Modelo '{key}' no está cargado.")

        X_embeddings = modelos["embeddings"]
        matriz_similitud = modelos["matriz"]
        cursos_data = modelos["cursos_info"]


        # --------------------------------------------------------
        # 2. Si cursos es una matriz .npy (X_final_cursos.npy)
        # --------------------------------------------------------
        if isinstance(cursos_data, np.ndarray):
            # Se requiere tener un archivo CSV descriptivo paralelo, por ejemplo:
            info_path = "data/cursos_info.csv"
            try:
                df_cursos = pd.read_csv(info_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"❌ No se pudo cargar información descriptiva de cursos ({info_path}). Error: {e}"
                )
        elif isinstance(cursos_data, pd.DataFrame):
            df_cursos = cursos_data
        else:
            raise HTTPException(
                status_code=400,
                detail="❌ El tipo de datos de 'cursos' no es válido (debe ser np.ndarray o DataFrame)."
            )

        # --------------------------------------------------------
        # 3. Calcular similitud TF-IDF sobre nombres de cursos
        # --------------------------------------------------------
        corpus = df_cursos['NOMBRE_OFERTA'].fillna('').astype(str).tolist()
        vect = TfidfVectorizer(max_features=5000)
        tfidf_matrix = vect.fit_transform(corpus)
        query_vec = vect.transform([query])

        sims_tfidf = cosine_similarity(query_vec, tfidf_matrix)[0]

        # --------------------------------------------------------
        # 4. Calcular similitud en espacio de embeddings
        # --------------------------------------------------------
        top_indices = np.argsort(sims_tfidf)[::-1][:10]
        q_vec_embed = X_embeddings[top_indices].mean(axis=0).reshape(1, -1)
        sims_embed = cosine_similarity(q_vec_embed, X_embeddings)[0]

        # --------------------------------------------------------
        # 5. Combinar resultados (ajustable)
        # --------------------------------------------------------
        similitud_final = 0.6 * sims_embed + 0.4 * sims_tfidf

        # --------------------------------------------------------
        # 6. Seleccionar top recomendaciones
        # --------------------------------------------------------
        top_indices = np.argsort(similitud_final)[::-1][:num_recomendaciones]
        resultados = df_cursos.iloc[top_indices][['NOMBRE_OFERTA', 'MODALIDAD', 'TIPO_OFERTA']].drop_duplicates()

        return resultados.to_dict(orient="records")
    
# ============================================================
# SINGLETON INSTANCE
# ============================================================
recommender_service = RecommenderService()
