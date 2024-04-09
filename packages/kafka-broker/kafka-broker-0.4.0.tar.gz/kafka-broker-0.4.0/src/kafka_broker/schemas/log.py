from typing import Any
import uuid
from pydantic import BaseModel

from src.kafka_broker.enums import EventStatus


class Log(BaseModel):
    correlation_id: uuid.UUID
    status: EventStatus
    level: int
    module: str
    message: str
    store:  dict[str, Any] = {}
    sequence: list[str] = []
    job_id: int | None = None