
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelMissionOptionsResourcesCombinations import MissionOptionsResourcesCombinations

class OptionsResourcesCombination:
    def return_mission_options_resources_combinations(self, assets: list[Asset], care_facilities: list[CareFacility],
                                                      mission_options_assets: list[MissionOptionsAssets], mission_requirements: list[MissionRequirements])\
            -> list[MissionOptionsResourcesCombinations]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")