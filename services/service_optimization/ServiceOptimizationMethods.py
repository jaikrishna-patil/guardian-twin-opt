from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.ModelConstraints import Constraint
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

class OptimizationMethods:

    def return_final_assignments_multiple_obj(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list):
        raise NotImplementedError("Not implemented!!!")
    def return_final_assignments_single_obj(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list):
        raise NotImplementedError("Not implemented!!!")
    def return_final_assignments_single_obj_scheduler(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list):
        raise NotImplementedError("Not implemented!!!")
    def return_final_assignments_multiple_obj_multiple_constraints(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list, constraints: dict):
        raise NotImplementedError("Not implemented!!!")

    def return_final_assignments_multiple_obj_scheduler(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list):
        raise NotImplementedError("Not implemented!!!")
