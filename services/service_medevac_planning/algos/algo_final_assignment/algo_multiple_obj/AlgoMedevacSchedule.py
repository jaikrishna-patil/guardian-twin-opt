import pandas as pd

from services.service_medevac_planning.ServiceMedevacPlanning import MedevacPlanningMethods
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

from services.models.ModelSettings import Settings

from services.service_medevac_planning.algos.algo_final_assignment.algo_multiple_obj.medevac_helpers import MedevacHelper
class MedevacSchedule(MedevacPlanningMethods):
    """
    A class for planning medical evacuation (MEDEVAC) operations.

    This class extends MedevacPlanningMethods and uses MedevacHelper to perform
    various steps in the MEDEVAC planning process, including triage scoring,
    optimization problem framing, and assignment generation for both urgency-based
    and reverse triage scenarios.

    Attributes:
        helper (MedevacHelper): An instance of MedevacHelper used for various
        MEDEVAC planning operations, including triage scoring, filtering, optimization,
        and final schedule generation.

    Methods:
        return_medevac_schedule: Generates a MEDEVAC schedule based on
        given missions, assets, care facilities, and settings, supporting either urgency-based
        or reverse triage types based on user input.
    """
    def __init__(self):
        """
        Initialize the MedevacSchedule instance with a MedevacHelper.
        """
        self.helper = MedevacHelper()  # Create an instance of MedevacHelper

    def return_medevac_schedule(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], settings: Settings):
        """
        Generate a MEDEVAC schedule based on the given missions, assets, care facilities, and settings.

        This method performs the following steps:
        1. Initialize PyReason and generate triage scores for all casualties involved in the mission.
        2. Filter and update casualty information based on triage scores to identify the most urgent.
        3. Frame optimization problems for the filtered set of casualties, assets, and care facilities.
        4. Run optimization instances to get initial assignment plan for possible casualty and asset.
        5. Generate final assignments and create a reasoned comparison between solutions using PyReason for initial assignments.
        6. Offer the user a choice between urgency-based and reverse triage schedules, if both are valid.
        7. Generate the future MEDEVAC schedule based on the user's choice.

        Args:
            missions_options (list[MissionOptionsAssets]): List of mission options with associated assets.
            assets (list[Asset]): List of available assets for MEDEVAC operations.
            care_facilities (list[CareFacility]): List of available care facilities.
            settings (Settings): Configuration settings for the MEDEVAC planning process.

        Returns:
            dict: A final MEDEVAC schedule based on either urgency-based or reverse triage assignments, depending on the user's selection.
            {
            (asset name, asset current location, casualty, asset destination location/care facility): (start timestep, end timestep(hours))
            }

        """



        dict_triage_scores = self.helper.initialize_pyreason(missions_options=missions_options, assets=assets, care_facilities= care_facilities, settings = settings)
        filtered_missions = self.helper.get_filtered_casualties_info(dict_triage_scores=dict_triage_scores, missions_options=missions_options)

        dict_optimization_instances = self.helper.frame_opt_problems(missions_options=filtered_missions, assets=assets, care_facilities= care_facilities)
        dict_optimization_results = self.helper.run_optimization_instances(dict_optimization_instances = dict_optimization_instances)
        final_assignments_plan = self.helper.get_final_assignments(dict_optimization_results=dict_optimization_results)

        assignment_urgency = final_assignments_plan.urgency_plan
        assignment_reverse = final_assignments_plan.reverse_plan
        schedule_urgency, schedule_reverse = False, False
        if not pd.isna(assignment_urgency):
            schedule_urgency = True
            print('Urgency/Triage score based initial Assignment')
            for cas, (asset, cf, ts) in assignment_urgency.items():
                print(f'{cas}: ({asset}, {cf})')
        if not pd.isna(assignment_reverse):
            schedule_reverse = True
            print('Reverse/ Return time to duty based initial Assignment')
            for cas, (asset, cf, ts) in assignment_reverse.items():
                print(f'{cas}: ({asset}, {cf})')
        if schedule_urgency and schedule_reverse:
            choice = ''
            while choice not in ['1', '2']:
                print("Choose the type of schedule you want to generate:")
                print("1. Urgency based")
                print("2. Reverse")
                choice = input("Enter 1 or 2: ")
            if choice == '1':
                schedule_type = 'urgency'
            elif choice == '2':
                schedule_type = 'reverse'

        final_schedule = self.helper.generate_future_medevac_schedule(dict_optimization_instances=dict_optimization_instances, dict_optimization_results=dict_optimization_results, schedule_type=schedule_type)
        return final_schedule





