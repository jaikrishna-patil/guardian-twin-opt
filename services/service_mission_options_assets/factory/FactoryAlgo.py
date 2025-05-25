from services.service_mission_options_assets.algos.pyreason.algo_mission_options_assets_basic.AlgoMissionOptionsAssetsBasic import MissionOptionsAssetsBasic
from services.service_mission_options_assets.algos.pyreason.algo_mission_options_assets_basic.AlgoMissionOptionsAssetsRange import MissionOptionsAssetsRange
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class MissionrequirementsToMissionoptionsAssetsAlgoName(Enum):
    BASIC = "basic"
    RANGE = "range"

class MissionrequirementsToMissionoptionsAssetsFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_missionrequirements_to_missionoptionsAssets_algo(mode:str):
        if mode == MissionrequirementsToMissionoptionsAssetsAlgoName.BASIC:
            return MissionOptionsAssetsBasic()
        elif mode == MissionrequirementsToMissionoptionsAssetsAlgoName.RANGE:
            return MissionOptionsAssetsRange()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")