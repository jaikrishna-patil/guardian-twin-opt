from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

class MedevacPlanningMethods:


    def return_medevac_plan(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility],
                            settings):
        raise NotImplementedError("Not implemented!!!")

    def return_medevac_schedule(self, missions_options: list[MissionOptionsAssets], assets: list[Asset],
                            care_facilities: list[CareFacility],
                            settings):
        raise NotImplementedError("Not implemented!!!")

