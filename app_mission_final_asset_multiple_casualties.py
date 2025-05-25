
from services.service_mission_final_assets.factory.FactoryAlgo import MissionoptionsAssetsToMissionfinalAssetsFactory, MissionoptionsAssetsToMissionfinalAssetsAlgoName
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets


if __name__ == "__main__":



    mission1 = MissionOptionsAssets(patient_name='Adrian Monk', assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 20)
    mission2 = MissionOptionsAssets(patient_name='Natalie Tieger', assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165'], triage_score = 10)
    mission3 = MissionOptionsAssets(patient_name='Leland Stottlemeyer', assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165'], triage_score = 20)
    mission4 = MissionOptionsAssets(patient_name='Jake Peralta', assets_possible=['Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 30)
    mission5 = MissionOptionsAssets(patient_name='Sharona Fleming', assets_possible=['Chinook CH99', 'Truck M1165'], triage_score = 40)

    mission6 = MissionOptionsAssets(patient_name='Randy Disher', assets_possible=['Black hawk HH60M', 'Chinook CH47'], triage_score = 43)
    mission7 = MissionOptionsAssets(patient_name='Trudy Monk', assets_possible=['Chinook CH47', 'Chinook CH99'], triage_score = 13)
    mission8 = MissionOptionsAssets(patient_name='Charles Kroger', assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 95)
    mission9 = MissionOptionsAssets(patient_name='Julie Trieger', assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 84)
    mission10 = MissionOptionsAssets(patient_name='Benjy Fleming', assets_possible=['Black hawk HH60M', 'Chinook CH47', 'Chinook CH99', 'Truck M1165', 'Ambulance M997A3'], triage_score = 82)

    all_mission_options = [mission1, mission2, mission3, mission4, mission5, mission6, mission7, mission8, mission9, mission10]
    print("")
    print("ALGO :: Mission options assets -> Mission final asset")
    algo_mission_assets = MissionoptionsAssetsToMissionfinalAssetsFactory.create_missionoptionsAssets_to_missionfinalAssets_algo(mode=MissionoptionsAssetsToMissionfinalAssetsAlgoName.BASIC)
    assets_all_missions = algo_mission_assets.return_mission_final_asset(missions_options=all_mission_options)
    for mission_asset in assets_all_missions:
        print('\n')
        print(f"Patient {mission_asset.patient_name} is finally assigned following asset: {mission_asset}")



