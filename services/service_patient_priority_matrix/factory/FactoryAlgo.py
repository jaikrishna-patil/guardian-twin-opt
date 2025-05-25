from services.service_patient_priority_matrix.algos.pyreason.algo_patient_matrix_basic.AlgoPatientMatrixBasic import PatientMatrixBasic
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class TriagecategoryToPatientMatrixAlgoName(Enum):
    BASIC = "basic"

class TriagecategoryToPatientmatrixFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_triageCategory_to_patientMatrix_algo(mode:str):
        if mode == TriagecategoryToPatientMatrixAlgoName.BASIC:
            return PatientMatrixBasic()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")