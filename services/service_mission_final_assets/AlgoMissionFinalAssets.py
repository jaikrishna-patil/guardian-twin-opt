from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.ModelConstraints import Constraint
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

class FinalAssets:
    def return_mission_final_asset(self, missions_options: list[MissionOptionsAssets])\
            -> list[MissionFinalAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")
    def return_mission_final_asset_opt(self, missions_options: list[MissionOptionsAssets], constraints:list[Constraint])\
            -> list[MissionFinalAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")
    def return_mission_final_asset_scheduler(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities = list[CareFacility])-> list[MissionFinalAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")

    def return_mission_final_asset_triage(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], primary_triage: bool, reverse_triage: bool, situational_triage:bool)-> list[MissionFinalAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")
    def return_mission_final_asset_primary(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility]):
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")
    def return_mission_final_asset_OptConstraints(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], weight_available_ts: float, weight_need_equipment:float)-> list[MissionFinalAssets]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")