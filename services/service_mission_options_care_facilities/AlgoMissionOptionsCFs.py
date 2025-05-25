
from services.models.ModelCareFacility import CareFacility
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelMissionOptionsCFs import MissionOptionsCFs

class OptionsCFs:
    def return_mission_options_care_facilities(self, mission_requirements: list[MissionRequirements], care_facilities: list[CareFacility])\
            -> list[MissionOptionsCFs]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")