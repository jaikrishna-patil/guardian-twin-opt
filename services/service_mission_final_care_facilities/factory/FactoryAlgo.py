
from services.service_mission_final_care_facilities.algos.pyreason.algo_mission_final_cfs_basic.AlgoMissionFinalCFsBasic import MissionFinalCFsBasic
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class MissionoptionsCFsToMissionfinalCFsAlgoName(Enum):
    BASIC = "basic"

class MissionoptionsCFsToMissionfinalCFsFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_missionoptionsCFs_to_missionfinalCFs_algo(mode:str):
        if mode == MissionoptionsCFsToMissionfinalCFsAlgoName.BASIC:
            return MissionFinalCFsBasic()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")