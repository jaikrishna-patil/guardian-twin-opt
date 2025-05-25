from services.service_mission_options_care_facilities.algos.pyreason.algo_mission_options_care_facilities_basic.AlgoMissionOptionsCFsBasic import MissionOptionsCFsBasic
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class MissionrequirementsToMissionoptionsCFsAlgoName(Enum):
    BASIC = "basic"

class MissionrequirementsToMissionoptionsCFsFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_missionrequirements_to_missionoptionsCFs_algo(mode:str):
        if mode == MissionrequirementsToMissionoptionsCFsAlgoName.BASIC:
            return MissionOptionsCFsBasic()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")