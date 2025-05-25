from typing import List, Optional, Any

from pydantic import BaseModel
from pydantic import BaseModel, ValidationError, field_validator


class RationaleRecord(BaseModel):
    triage_score: Optional[float]
    threshold: Optional[Any]

class Option(BaseModel):
    input: str
    description: str
class TriageScore(BaseModel):
    algo_name: str
    value: float
class Interaction(BaseModel):
    question: str
    options: List[Option]

class TriageCategory(BaseModel):
    patient_name: str
    datetime_seconds: Optional[int]
    algo_name: Optional[str]
    category: str
    confidence: Optional[float]
    rationale: Optional[List[RationaleRecord]]
    interaction: Optional[Interaction]

    # Custom validator example (optional)
    @field_validator('confidence')
    def check_positive(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f'{field.field_name} must be a positive number')
        return v