
from services.service_medevac_planning.ServiceMedevacPlanning import MedevacPlanningMethods
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

from services.models.ModelSettings import Settings

from services.service_medevac_planning.algos.algo_final_assignment.algo_multiple_obj.medevac_helpers import MedevacHelper
class MedevacPlanning(MedevacPlanningMethods):
    """
    A class for planning medical evacuation (MEDEVAC) operations.

    This class extends MedevacPlanningMethods and uses MedevacHelper to perform
    various steps in the MEDEVAC planning process, including triage scoring,
    optimization problem framing, and assignment generation.

    Attributes:
        helper (MedevacHelper): An instance of MedevacHelper used for various MEDEVAC planning operations.

    Methods:
        return_medevac_plan: Generates a MEDEVAC plan based on given missions, assets, care facilities, and settings.
    """
    def __init__(self):
        """
                Initialize the MedevacPlanning instance with a MedevacHelper.
                """
        self.helper = MedevacHelper()  # Create an instance of MedevacHelper

    def return_medevac_plan(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], settings: Settings):
        """
               Generate a MEDEVAC plan based on the given missions, assets, care facilities, and settings.

               This method performs the following steps:
               1. Initialize PyReason and generate triage scores.
               2. Filter and update casualty information based on triage scores.
               3. Frame optimization problems.
               4. Run optimization instances.
               5. Generate final assignments and reason over the differences in solutions using pyreason.

               Args:
                   missions_options (list[MissionOptionsAssets]): List of mission options with associated assets.
                   assets (list[Asset]): List of available assets for MEDEVAC operations.
                   care_facilities (list[CareFacility]): List of available care facilities.
                   settings (Settings): Configuration settings for the MEDEVAC planning process.

               Returns:
                   Plan: A Plan object containing the final assignments for urgency and reverse triage based on input settings.
               """
        dict_triage_scores = self.helper.initialize_pyreason(missions_options=missions_options, assets=assets, care_facilities= care_facilities, settings = settings)
        filtered_missions = self.helper.get_filtered_casualties_info(dict_triage_scores=dict_triage_scores, missions_options=missions_options)

        dict_optimization_instances = self.helper.frame_opt_problems(missions_options=filtered_missions, assets=assets, care_facilities= care_facilities)
        dict_optimization_results = self.helper.run_optimization_instances(dict_optimization_instances = dict_optimization_instances)

        final_assignments_plan = self.helper.get_final_assignments(dict_optimization_results=dict_optimization_results)

        return final_assignments_plan



