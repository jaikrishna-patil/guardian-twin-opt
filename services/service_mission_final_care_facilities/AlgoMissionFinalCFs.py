from services.models.ModelMissionOptionsCFs import MissionOptionsCFs
from services.models.ModelMissionFinalCFs import MissionFinalCFs

class FinalCareFacilities:
    def return_mission_final_care_facility(self, missions_options: list[MissionOptionsCFs])\
            -> list[MissionFinalCFs]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")