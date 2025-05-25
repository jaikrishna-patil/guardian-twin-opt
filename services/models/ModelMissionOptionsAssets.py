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

class MissionOptionsAssets(BaseModel):
    patient_name: Optional[str]
    location: Optional[list]=None
    assets_possible: Optional[list]=None
    care_facilities_possible: Optional[list]=None
    datetime_seconds: int = int(datetime.now().timestamp())
    algo_name: str = 'pyreason_basic'
    insults_dict: dict = None
    vitals_dict: dict = None
    triage_score: Optional[float] = None
    triage_category: Optional[str] = None
    lsi_ts: Optional[float] = None
    rtd_ts: Optional[float] = None
    equipments_needed: Optional[float] = None
    need_equipments: Optional[float] = None
    assets_details: Optional[dict] = None
    confidence: float = 1.0
    rationale: Optional[List[RationaleRecord]] = None
    interaction: Optional[Interaction] = None

    # Custom validator example (optional)
    @field_validator('confidence')
    def check_positive(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f'{field.field_name} must be a positive number')
        return v