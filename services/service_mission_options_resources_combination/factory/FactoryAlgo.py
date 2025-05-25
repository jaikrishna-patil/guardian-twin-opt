
from services.service_mission_options_resources_combination.algos.pyreason.algo_mission_options_resources_combinations_basic.AlgoMissionOptionsResourcesCombinationsBasic import MissionOptionsResourcesCombinationBasic
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class MissionrequirementsToMissionoptionsResourcesAlgoName(Enum):
    BASIC = "basic"

class MissionrequirementsToMissionoptionsResourcesFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_missionrequirements_to_missionoptionsresources_algo(mode:str):
        if mode == MissionrequirementsToMissionoptionsResourcesAlgoName.BASIC:
            return MissionOptionsResourcesCombinationBasic()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")