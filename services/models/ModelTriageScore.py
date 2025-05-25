from typing import List, Optional, Any

from pydantic import BaseModel
from pydantic import BaseModel, ValidationError, field_validator

class Vital(BaseModel):
    name: str
    value: float

class RationaleRecord(BaseModel):
    score: Optional[float]
    vital: Optional[Vital]
    threshold: Optional[Any]

class Option(BaseModel):
    input: str
    description: str

class Interaction(BaseModel):
    question: str
    options: List[Option]

class TriageScore(BaseModel):
    patient_name: Optional[str]
    datetime_seconds: int
    algo_name: str
    score: float
    confidence: float
    rationale: List[RationaleRecord]
    interaction: Optional[Interaction]

    # Custom validator example (optional)
    @field_validator('score', 'confidence')
    def check_positive(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f'{field.field_name} must be a positive number')
        return v