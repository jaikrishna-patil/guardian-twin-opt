from typing import List, Optional, Any

from pydantic import BaseModel
from pydantic import BaseModel, ValidationError, field_validator


class RationaleRecord(BaseModel):
    triage_category: Optional[str]
    threshold: Optional[Any]

class Option(BaseModel):
    input: str
    description: str
class TriageCategory(BaseModel):
    algo_name: str
    value: float
class Interaction(BaseModel):
    question: str
    options: List[Option]

class PatientMatrix(BaseModel):
    patient_name: Optional[str]
    datetime_seconds: int
    algo_name: str
    litter: bool
    ambulatory: bool
    medevac_needed: bool
    medevac_priority: Optional[int]
    evac_needed: bool
    evac_priority: Optional[int]
    resupply_needed: bool
    resupply_priority: Optional[int]
    confidence: float
    rationale: Optional[List[RationaleRecord]]
    interaction: Optional[Interaction]

    # Custom validator example (optional)
    @field_validator('confidence')
    def check_positive(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f'{field.field_name} must be a positive number')
        return v