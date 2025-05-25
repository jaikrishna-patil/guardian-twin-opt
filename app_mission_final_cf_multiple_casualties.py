
from services.service_mission_final_care_facilities.factory.FactoryAlgo import MissionoptionsCFsToMissionfinalCFsFactory, MissionoptionsCFsToMissionfinalCFsAlgoName
from services.models.ModelMissionOptionsCFs import MissionOptionsCFs


if __name__ == "__main__":



    mission1 = MissionOptionsCFs(patient_name='Adrian Monk', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 20)
    mission2 = MissionOptionsCFs(patient_name='Natalie Tieger', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 10)
    mission3 = MissionOptionsCFs(patient_name='Leland Stottlemeyer', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 20)
    mission4 = MissionOptionsCFs(patient_name='Jake Peralta', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 30)
    mission5 = MissionOptionsCFs(patient_name='Sharona Fleming', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 40)

    mission6 = MissionOptionsCFs(patient_name='Randy Disher', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 43)
    mission7 = MissionOptionsCFs(patient_name='Trudy Monk', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 13)
    mission8 = MissionOptionsCFs(patient_name='Charles Kroger', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 95)
    mission9 = MissionOptionsCFs(patient_name='Julie Trieger', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 84)
    mission10 = MissionOptionsCFs(patient_name='Benjy Fleming', care_facilities_possible=['Battlefield Medical Center', 'Noble Medical Center', 'Young hearts Medical Center'], triage_score = 82)

    all_mission_options = [mission1, mission2, mission3, mission4, mission5, mission6, mission7, mission8, mission9, mission10]
    print("")
    print("ALGO :: Mission options cfs -> Mission final cf")
    algo_mission_assets = MissionoptionsCFsToMissionfinalCFsFactory.create_missionoptionsCFs_to_missionfinalCFs_algo(mode=MissionoptionsCFsToMissionfinalCFsAlgoName.BASIC)
    cfs_all_missions = algo_mission_assets.return_mission_final_care_facility(missions_options=all_mission_options)
    for mission_cf in cfs_all_missions:
        print('\n')
        print(f"Patient {mission_cf.patient_name} is finally assigned following Care facility: {mission_cf}")



