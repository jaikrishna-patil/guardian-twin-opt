from services.service_triage_category.algos.pyreason.algo_triage_basic.AlgoTriageCategoryBasic import TriageCategoryBasic
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class TriagescoreToTriagecategoryAlgoName(Enum):
    BASIC = "basic"

class TriagescoreToTriagecategoryFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_triageScore_to_triageCategory_algo(mode:str,thresholds:Thresholds):
        if mode == TriagescoreToTriagecategoryAlgoName.BASIC:
            return TriageCategoryBasic(thresholds=thresholds)

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")