from services.service_triage.algos.vanilla.algo_triage_basic.AlgoBasicTriage import BasicTriage
from services.service_triage.algos.vanilla.algo_triage_basic2.AlgoBasicTriage2 import BasicTriage2
from services.service_triage.algos.vanilla.algo_triage_life.AlgoLifeTriage import LifeTriage
# from services.service_triage.algos.pyreason.algo_triage_pyreason.AlgoTriageLife import TriageLife
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]


class TriageAlgoName(Enum):
    BASIC = "basic"
    BASIC2 = "basic2"
    LIFE = "life"

class TriageFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_triage_algo(mode:str,thresholds:Thresholds):
        if mode == TriageAlgoName.BASIC:
            return BasicTriage(thresholds=thresholds)

        elif mode == TriageAlgoName.BASIC2:
            return BasicTriage2(thresholds=thresholds)

        elif mode == TriageAlgoName.LIFE:
            return LifeTriage(thresholds=thresholds)

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")

