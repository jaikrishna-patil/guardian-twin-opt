from typing import List, Optional, Any

from pydantic import BaseModel
from pydantic import BaseModel, ValidationError, field_validator
from datetime import datetime

class RationaleRecord(BaseModel):
    triage_category: Optional[str]
    threshold: Optional[Any]
class Option(BaseModel):
    input: str
    description: str

class Interaction(BaseModel):
    question: str
    options: List[Option]

class MissionFinalCFs(BaseModel):
    patient_name: Optional[str]
    datetime_seconds: int = int(datetime.now().timestamp())
    algo_name: str = 'pyreason_basic'
    cf_final: str = ''
    cf_details: Optional[dict] = None
    confidence: float = 1.0
    rationale: Optional[List[RationaleRecord]] = None
    interaction: Optional[Interaction] = None

    # Custom validator example (optional)
    @field_validator('confidence')
    def check_positive(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f'{field.field_name} must be a positive number')
        return v