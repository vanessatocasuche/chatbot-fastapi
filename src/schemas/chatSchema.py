from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Modelo de entrada para enviar un mensaje al chatbot."""
    message: str = Field(..., description="Mensaje enviado por el usuario al chatbot.")
    id_conversation: Optional[int] = Field(
        None,
        description="Identificador opcional de la conversación actual."
    )


class ChatResponse(BaseModel):
    """Modelo de salida con la respuesta del chatbot."""
    content: str = Field(..., description="Respuesta generada por el chatbot.")
    cluster_id: Optional[int] = Field(
        None,
        description="Identificador del clúster o tema detectado (si aplica)."
    )
    id_conversation: Optional[int] = Field(
        None,
        description="ID de la conversación asociada a este intercambio."
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza del modelo (entre 0 y 1)."
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Marca de tiempo en la que se generó la respuesta."
    )


class FeedbackRequest(BaseModel):
    """Modelo de entrada para enviar retroalimentación de un mensaje."""
    id_message: int = Field(..., description="Identificador del mensaje asociado.")
    feedback: str = Field(..., description="Comentario o evaluación del usuario sobre la respuesta del chatbot.")
    sentiment: Optional[str] = Field(None, description="Sentimiento detectado (positivo, negativo, neutro).")
    topic: Optional[str] = Field(None, description="Tema o categoría asociada al feedback.")
    keywords: Optional[str] = Field(None, description="Palabras clave identificadas en el feedback.")


class FeedbackResponse(BaseModel):
    """Modelo de salida después de almacenar la retroalimentación."""
    message: str = Field(..., description="Mensaje de confirmación del almacenamiento del feedback.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Marca de tiempo del registro del feedback.")
