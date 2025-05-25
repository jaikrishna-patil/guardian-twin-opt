#
# from services.service_mission_final_assets.factory.FactoryAlgo import MissionoptionsAssetsToMissionfinalAssetsFactory, MissionoptionsAssetsToMissionfinalAssetsAlgoName
# from services.models.ModelConstraints import Constraint
# from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
# from services.models.ModelAsset import Asset
# from services.models.ModelCareFacility import CareFacility
#
#
# if __name__ == "__main__":
#
#
#
#     mission1 = MissionOptionsAssets(patient_name='Adrian Monk', location= [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 20, available_ts = 4.5)
#     mission2 = MissionOptionsAssets(patient_name='Natalie Tieger', location = [47.9931, 8.2454], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 10, available_ts = 5.5)
#     mission3 = MissionOptionsAssets(patient_name='Leland Stottlemeyer', location = [46.4868, 2.4128], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165'], triage_score = 20, available_ts = 3.5)
#     mission4 = MissionOptionsAssets(patient_name='Jake Peralta', location = [49.8675, 0.6713], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 30, available_ts = 6.5)
#     mission5 = MissionOptionsAssets(patient_name='Sharona Fleming', location = [50.0087, 5.4571], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Chinook CH99', 'Truck M1165'], triage_score = 40, available_ts = 8.5)
#
#     mission6 = MissionOptionsAssets(patient_name='Randy Disher', location = [44.5857, 3.8395], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47'], triage_score = 43, available_ts = 0.5)
#     mission7 = MissionOptionsAssets(patient_name='Trudy Monk', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Chinook CH47', 'Chinook CH99'], triage_score = 13, available_ts = 0.5)
#     mission8 = MissionOptionsAssets(patient_name='Charles Kroger', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 95, available_ts = 1)
#     mission9 = MissionOptionsAssets(patient_name='Julie Trieger', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 84, available_ts = 0.5)
#     mission10 = MissionOptionsAssets(patient_name='Benjy Fleming', location = [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center',
#                                                            'Young hearts Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 82, available_ts = 1)
#
#     # Assets
#     asset1 = Asset(asset_name='Black hawk HH60M', asset_range_in_km=11670, asset_speed_kmph=100, location=[48.5325, 0.1321])
#     asset2 = Asset(asset_name='Chinook CH47', asset_type='vtol', asset_range_in_km=670, asset_speed_kmph=300, location=[46.6568, 1.7397])
#     asset3 = Asset(asset_name='Ambulance M997A3', asset_type='ground', asset_range_in_km=900, asset_speed_kmph=100,location=[48.3090, 6.5731])
#     asset4 = Asset(asset_name='Truck M1165', asset_type='ground', asset_range_in_km=800, asset_speed_kmph=180, location=[48.5620, 2.2945])
#     asset5 = Asset(asset_name='Chinook CH99', asset_type='ctol', asset_range_in_km=670, asset_speed_kmph=90, location=[48.5620, 2.2945])
#
#     cf1 = CareFacility(cf_name='Battlefield Medical Center', location=[50.9757, 2.2945])
#
#     cf2 = CareFacility(cf_name='Noble Medical Center', location=[47.2275, 4.4509])
#
#     cf3 = CareFacility(cf_name='Young hearts Medical Center', location=[47.8607, 0.2802])
#
#
#
#     all_mission_options = [mission1, mission2, mission3, mission4, mission5, mission6, mission7, mission8, mission9, mission10]
#     all_assets = [asset1, asset2, asset3, asset4, asset5]
#     all_care_facilities = [cf1, cf2, cf3]
#     print("")
#     print("ALGO :: Mission options assets -> Mission final asset")
#     algo_mission_assets = MissionoptionsAssetsToMissionfinalAssetsFactory.create_missionoptionsAssets_to_missionfinalAssets_algo(mode=MissionoptionsAssetsToMissionfinalAssetsAlgoName.TRIAGE)
#     assets_all_missions = algo_mission_assets.return_mission_final_asset_triage(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
#     # for mission_asset in assets_all_missions:
#     #     print('\n')
#     #     print(f"Patient {mission_asset.patient_name} is finally assigned following schedule: {mission_asset}")
#
#
#

from services.service_mission_final_assets.factory.FactoryAlgo import MissionoptionsAssetsToMissionfinalAssetsFactory, MissionoptionsAssetsToMissionfinalAssetsAlgoName
from services.models.ModelConstraints import Constraint
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility


if __name__ == "__main__":



    mission1 = MissionOptionsAssets(patient_name='Ben Stokes', location= [48.8584, 2.2945], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99'], triage_score = 20, available_ts = 4.5)
    mission2 = MissionOptionsAssets(patient_name='Steve Smith', location = [47.9931, 8.2454], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', ], triage_score = 10, available_ts = 4)
    mission3 = MissionOptionsAssets(patient_name='Mike Hussey', location = [46.4868, 2.4128], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center'], assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99'], triage_score = 40, available_ts = 8.5)
    mission4 = MissionOptionsAssets(patient_name='Viv Richards', location = [49.8675, 0.6713], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center'], assets_possible=['Chinook CH99','Black hawk HH60M'], triage_score = 90, available_ts = 0.5)
    mission5 = MissionOptionsAssets(patient_name='Sharona Fleming', location = [50.0087, 5.4571], care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center'], assets_possible=['Chinook CH47'], triage_score = 5, available_ts = 0.5)

    # Assets
    asset1 = Asset(asset_name='Black hawk HH60M', asset_range_in_km=11670, asset_speed_kmph=100, location=[48.5325, 0.1321])
    asset2 = Asset(asset_name='Chinook CH47', asset_type='vtol', asset_range_in_km=670, asset_speed_kmph=300, location=[46.6568, 1.7397])
    asset3 = Asset(asset_name='Chinook CH99', asset_type='ctol', asset_range_in_km=670, asset_speed_kmph=90, location=[48.5620, 2.2945])

    cf1 = CareFacility(cf_name='Battlefield Medical Center', location=[50.9757, 2.2945])

    cf2 = CareFacility(cf_name='Noble Medical Center', location=[47.2275, 4.4509])



    all_mission_options = [mission1, mission2, mission3, mission4, mission5]
    all_assets = [asset1, asset2, asset3]
    all_care_facilities = [cf1, cf2]
    print("")
    print("ALGO :: Mission options assets -> Mission final asset")
    algo_mission_assets = MissionoptionsAssetsToMissionfinalAssetsFactory.create_missionoptionsAssets_to_missionfinalAssets_algo(mode=MissionoptionsAssetsToMissionfinalAssetsAlgoName.TRIAGE)
    assets_all_missions = algo_mission_assets.return_mission_final_asset_triage(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    # for mission_asset in assets_all_missions:
    #     print('\n')
    #     print(f"Patient {mission_asset.patient_name} is finally assigned following schedule: {mission_asset}")



