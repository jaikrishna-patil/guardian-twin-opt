import time

from services.service_mission_options_assets.factory.FactoryAlgo import MissionrequirementsToMissionoptionsAssetsFactory
from services.service_mission_options_assets.factory.FactoryAlgo import MissionrequirementsToMissionoptionsAssetsAlgoName
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelMissionOptionsCFs import MissionOptionsCFs
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

import pandas as pd
import pyreason as pr
import os
import numba

if __name__ == "__main__":

    mission1 = MissionRequirements(name='Adrian Monk', location= [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = True, evac_needed = False, resupply_needed = False, require_vtol=True, require_ctol = False, require_ground_vehicle = False,
                                   litters_spaces_required = 2, ambulatory_spaces_required = 3, weather_condition = 'clear', day_mission = True, night_mission = False, require_iv_provisions = False,
                                   require_medical_monitoring_system = False, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = False)
    mission2 = MissionRequirements(name='Natalie Tieger', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = False, evac_needed = True, resupply_needed = False, require_vtol=False, require_ctol = True, require_ground_vehicle = False,
                                   litters_spaces_required = 0, ambulatory_spaces_required = 1, weather_condition = 'clear', day_mission = True, night_mission = False, require_iv_provisions = False,
                                   require_medical_monitoring_system = False, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = False)
    mission3 = MissionRequirements(name='Leland Stottlemeyer', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = True, evac_needed = False, resupply_needed = False, require_vtol=True, require_ctol = False, require_ground_vehicle = False,
                                   litters_spaces_required = 1, ambulatory_spaces_required = 0, weather_condition = 'clear', day_mission = True, night_mission = False, require_iv_provisions = False,
                                   require_medical_monitoring_system = True, require_life_support_equipment = False, require_oxygen_generation_system = True, require_patient_litter_lift_system = True)
    mission4 = MissionRequirements(name='Jake Peralta', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = True, evac_needed = False, resupply_needed = False, require_vtol=True, require_ctol = False, require_ground_vehicle = False,
                                   litters_spaces_required = 1, ambulatory_spaces_required = 0, weather_condition = 'clear', day_mission = True, night_mission = True, require_iv_provisions = True,
                                   require_medical_monitoring_system = True, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = True)
    mission5 = MissionRequirements(name='Sharona Fleming', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = True, evac_needed = False, resupply_needed = False, require_vtol=False, require_ctol = True, require_ground_vehicle = False,
                                   litters_spaces_required = 1, ambulatory_spaces_required = 0, weather_condition = 'clear', day_mission = True, night_mission = False, require_iv_provisions = True,
                                   require_medical_monitoring_system = True, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = True)

    mission6 = MissionRequirements(name='Randy Disher', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = True, evac_needed = False, resupply_needed = False, require_vtol=True, require_ctol = False, require_ground_vehicle = False,
                                   litters_spaces_required = 1, ambulatory_spaces_required = 0, weather_condition = 'unclear', day_mission = True, night_mission = False, require_iv_provisions = True,
                                   require_medical_monitoring_system = True, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = True)
    mission7 = MissionRequirements(name='Trudy Monk', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = False, evac_needed = True, resupply_needed = False, require_vtol=False, require_ctol = True, require_ground_vehicle = False,
                                   litters_spaces_required = 0, ambulatory_spaces_required = 1, weather_condition = 'clear', day_mission = True, night_mission = False, require_iv_provisions = False,
                                   require_medical_monitoring_system = False, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = False)
    mission8 = MissionRequirements(name='Charles Kroger', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = False, evac_needed = True, resupply_needed = False, require_vtol=False, require_ctol = False, require_ground_vehicle = True,
                                   litters_spaces_required = 0, ambulatory_spaces_required = 1, weather_condition = 'unclear', day_mission = True, night_mission = True, require_iv_provisions = False,
                                   require_medical_monitoring_system = False, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = False)
    mission9 = MissionRequirements(name='Julie Trieger', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = False, evac_needed = True, resupply_needed = False, require_vtol=False, require_ctol = False, require_ground_vehicle = True,
                                   litters_spaces_required = 0, ambulatory_spaces_required = 1, weather_condition = 'clear', day_mission = True, night_mission = False, require_iv_provisions = False,
                                   require_medical_monitoring_system = False, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = False)
    mission10 = MissionRequirements(name='Benjy Fleming', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
                                                           'Young hearts Medical Center'], medevac_needed = False, evac_needed = True, resupply_needed = False, require_vtol=False, require_ctol = False, require_ground_vehicle = True,
                                   litters_spaces_required = 0, ambulatory_spaces_required = 1, weather_condition = 'clear', day_mission = True, night_mission = True, require_iv_provisions = False,
                                   require_medical_monitoring_system = False, require_life_support_equipment = False, require_oxygen_generation_system = False, require_patient_litter_lift_system = False)

    asset1 = Asset(asset_name = 'Black hawk HH60M', asset_type = 'vtol', asset_range_in_km = 670, asset_speed_kmph=280, location = [48.5620, 2.2945], asset_status = 'available', asset_mission_type = 'medevac', crew = ['pilot', 'copilot', 'crew_chief', 'medic_1'], litter_capacity = 6,
                   ambulatory_capacity = 6, operational_day = True, operational_night=True, operational_adverse_weather = True, has_iv_provisions = True, has_medical_monitoring_system = True,
                   has_life_support_equipment = True, has_oxygen_generation_system = True, has_patient_litter_lift_system = True)
    asset2 = Asset(asset_name = 'Chinook CH47', asset_type = 'vtol', asset_range_in_km = 670, asset_speed_kmph=280,  location = [48.5620, 2.2945], asset_status = 'available', asset_mission_type = 'medevac', crew = ['pilot', 'copilot', 'crew_chief', 'medic_1'], litter_capacity = 24,
                   ambulatory_capacity = 24, operational_day = True, operational_night=True, operational_adverse_weather = True, has_iv_provisions = True, has_medical_monitoring_system = True,
                   has_life_support_equipment = True, has_oxygen_generation_system = True, has_patient_litter_lift_system = True)
    asset3 = Asset(asset_name = 'Ambulance M997A3', asset_type = 'ground', asset_range_in_km = 670, asset_speed_kmph=280,  location = [48.5620, 2.2945], asset_status = 'available', asset_mission_type = 'medevac', crew = ['driver', 'medic_1', 'crew_chief'], litter_capacity = 4,
                   ambulatory_capacity = 4, operational_day = True, operational_night=True, operational_adverse_weather = False, has_iv_provisions = True, has_medical_monitoring_system = True,
                   has_life_support_equipment = True, has_oxygen_generation_system = True, has_patient_litter_lift_system = True)
    asset4 = Asset(asset_name = 'Truck M1165', asset_type = 'ground', asset_range_in_km = 670, asset_speed_kmph=280,  location = [48.5620, 2.2945], asset_status = 'available', asset_mission_type = 'evac', crew = ['driver'], litter_capacity = 0,
                   ambulatory_capacity = 12, operational_day = True, operational_night=True, operational_adverse_weather = True, has_iv_provisions = False, has_medical_monitoring_system = False,
                   has_life_support_equipment = False, has_oxygen_generation_system = False, has_patient_litter_lift_system = False)
    asset5 = Asset(asset_name = 'Chinook CH99', asset_type = 'ctol', asset_range_in_km = 670, asset_speed_kmph=280,  location = [48.5620, 2.2945], asset_status = 'available', asset_mission_type = 'evac', crew = ['pilot', 'copilot', 'crew_chief', 'medic_1'], litter_capacity = 0,
                   ambulatory_capacity = 10, operational_day = True, operational_night=True, operational_adverse_weather = True, has_iv_provisions = False, has_medical_monitoring_system = False,
                   has_life_support_equipment = False, has_oxygen_generation_system = False, has_patient_litter_lift_system = False)
    cf1 = CareFacility(cf_name='Battlefield Medical Center', location = [50.9757, 2.2945])

    cf2 = CareFacility(cf_name='Noble Medical Center', location = [50.9757, 2.2945])

    cf3 = CareFacility(cf_name='Young hearts Medical Center', location = [50.9757, 2.2945])

    all_cfs = [cf1, cf2, cf3]
    all_mission_reqs = [mission1, mission2, mission3, mission4, mission5, mission6, mission7, mission8, mission9, mission10]
    all_assets = [asset1, asset2, asset3, asset4, asset5]
    print("")
    print("ALGO :: Mission requirements -> Mission options assets")
    algo_mission_assets = MissionrequirementsToMissionoptionsAssetsFactory.create_missionrequirements_to_missionoptionsAssets_algo(mode=MissionrequirementsToMissionoptionsAssetsAlgoName.RANGE)
    assets_all_missions = algo_mission_assets.return_mission_options_assets_range(mission_requirements=all_mission_reqs, assets=all_assets, care_facilities=all_cfs)
    for mission in assets_all_missions:
        print('\n')
        print(f"Patient {mission.patient_name} can be assigned following resources: {mission}")



