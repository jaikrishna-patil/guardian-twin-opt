
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsBasic import MissionFinalAssetsBasic
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsMultipleOpt import MissionFinalAssetsMultipleOpt
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsScheduler import MissionFinalAssetsScheduler
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsTriage import MissionFinalAssetsTriage
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsPrimary import MissionFinalAssetsPrimary
from services.service_mission_final_assets.algos.pyreason.algo_mission_final_assets_basic.AlgoMissionFinalAssetsOptConstraints import MissionFinalAssetsOptConstraints
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class Threshold(BaseModel):
    min_value:float
    max_value:float
class Thresholds(BaseModel):
    thresholds: Dict[str, Threshold]

class MissionoptionsAssetsToMissionfinalAssetsAlgoName(Enum):
    BASIC = "basic"
    OPT = "multiple_opts"
    SCHEDULER = "scheduler"
    TRIAGE = "triage"
    PRIMARY = "primary"
    OPT_CONSTRAINTS = "opt_constraints"

class MissionoptionsAssetsToMissionfinalAssetsFactory:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_missionoptionsAssets_to_missionfinalAssets_algo(mode:str):
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.BASIC:
            return MissionFinalAssetsBasic()
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.OPT:
            return MissionFinalAssetsMultipleOpt()
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.SCHEDULER:
            return MissionFinalAssetsScheduler()
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.TRIAGE:
            return MissionFinalAssetsTriage()
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.PRIMARY:
            return MissionFinalAssetsPrimary()
        if mode == MissionoptionsAssetsToMissionfinalAssetsAlgoName.OPT_CONSTRAINTS:
            return MissionFinalAssetsOptConstraints()


        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")