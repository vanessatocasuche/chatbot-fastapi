from pydantic import BaseModel
from typing import Optional

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatRequest(BaseModel):
    """
    Modelo de entrada para enviar un mensaje al chatbot.
    """
    message: str = Field(..., description="Mensaje enviado por el usuario al chatbot.")
    # session_id: Optional[str] = Field(
    #     None,
    #     description="Identificador único de la sesión o conversación en curso."
    # )


class ChatResponse(BaseModel):
    """
    Modelo de salida con la respuesta del chatbot.
    """
    response: str = Field(..., description="Respuesta generada por el chatbot.")
    cluster_id: Optional[int] = Field(
        None,
        description="Identificador del clúster temático o de contexto detectado (si aplica)."
    )
    conversation_id: Optional[int] = Field(
        None,
        description="Identificador único de la conversación asociada a este intercambio."
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza del modelo (entre 0 y 1)."
    )
    created_at: Optional[str] = Field(
        default_factory=datetime.utcnow,
        description="Marca de tiempo del momento en que se generó la respuesta."
    )


class FeedbackRequest(BaseModel):
    """
    Modelo para almacenar retroalimentación de una conversación o respuesta.
    """
    conversation_id: int = Field(..., description="Identificador de la conversación.")
    feedback: str = Field(..., description="Comentario o evaluación del usuario.")
    sentiment: Optional[str] = Field(
        None,
        description="Sentimiento del feedback (por ejemplo: positivo, negativo, neutro)."
    )
    topic: Optional[str] = Field(
        None,
        description="Tema o categoría del feedback."
    )
    keywords: Optional[str] = Field(
        None,
        description="Palabras clave asociadas al feedback."
    )

class FeedbackResponse(BaseModel):
    """
    Modelo de respuesta después de almacenar la retroalimentación.
    """
    message: str = Field(..., description="Mensaje de confirmación del almacenamiento del feedback.")