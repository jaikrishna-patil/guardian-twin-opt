

from services.service_mission_final_assets.factory.FactoryAlgo import MissionoptionsAssetsToMissionfinalAssetsFactory, MissionoptionsAssetsToMissionfinalAssetsAlgoName
from services.models.ModelConstraints import Constraint
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility
import json
import random
import time
import tracemalloc
import pandas as pd
import argparse
import os

def main(n_casualties, n_assets, n_cfs):


    # cas_indexes = random.sample(range(1, 501), n_casualties)
    # assets_indexes = random.sample(range(1, 501), n_assets)
    # cfs_indexes = random.sample(range(1, 101), n_cfs)
    cas_indexes = [100,10,20,30,40,50,60,70,80,90]
    assets_indexes = [1,5,10,15,20,25]
    cfs_indexes = [1,5,10,15,20,25,30,35,40,50]
    # cas_indexes = [103, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    # assets_indexes = [11, 5, 10, 15, 20]
    # cfs_indexes = [1, 5, 10, 15, 20, 29, 30, 35, 37, 50]
    assets_possible = []
    cfs_possible = []
    all_mission_options = []
    all_assets = []
    all_care_facilities = []

    for i in assets_indexes:
        folder_p = 'data/asset_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        all_assets.append(Asset(asset_name=data['name'], asset_ground=data['ground'], asset_vtol=data['vtol'], crew_duty_hrs = data['crew_duty_hrs'], asset_range_in_km= data['range_km'], asset_speed_kmph=data['speed_kph'], location=[data['latitude'], data['longitude']]))
        assets_possible.append(data['name'])

    for i in cfs_indexes:
        folder_p = 'data/cf_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        all_care_facilities.append(CareFacility(cf_name=data['name'], location=[data['latitude'], data['longitude']]))
        cfs_possible.append(data['name'])

    for i in cas_indexes:
        folder_p = 'data/casualty_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        all_mission_options.append(MissionOptionsAssets(patient_name=data['name'], care_facilities_possible=cfs_possible, assets_possible=assets_possible, triage_score=data['triage_score'], rtd_ts= data['rtd_ts'], equipments_needed = data['equipments_needed'],
                                                        location=[data['latitude'], data['longitude']]))

    # print("")
    # print("ALGO :: Mission options assets -> Mission final asset")
    algo_mission_assets = MissionoptionsAssetsToMissionfinalAssetsFactory.create_missionoptionsAssets_to_missionfinalAssets_algo(mode=MissionoptionsAssetsToMissionfinalAssetsAlgoName.PRIMARY)
    start = time.time()
    tracemalloc.start()
    (assets_all_missions, num_iterations, accepted_triage, initial_limit_vtol,
     (primary_sol_primary_obj, reverse_sol_primary_obj, situational_sol_primary_obj),
     (primary_sol_reverse_obj, reverse_sol_reverse_obj, situational_sol_reverse_obj),
     (primary_sol_situational_obj, reverse_sol_situational_obj, situational_sol_situational_obj)) = algo_mission_assets.return_mission_final_asset_triage(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities, primary_triage = True, reverse_triage=True, situational_triage= True)
    t = round(time.time() - start, 3)
    mem = round(tracemalloc.get_traced_memory()[1] / (10 ** 6), 3)
    tracemalloc.stop()
    print('TIME:', t)
    print('MEMORY:', mem)
    # for mission_asset in assets_all_missions:
    #     print('\n')
    #     print(f"Patient {mission_asset.patient_name} is finally assigned following schedule: {mission_asset}")
    if len(assets_all_missions) > 0:
        solution_found = 1
    else:
        solution_found = 0
    num_casualties_served = len(assets_all_missions)


    # Create a DataFrame with the required data
    df = pd.DataFrame({
        'num_cas': [n_casualties],
        'num_assets': [n_assets],
        'time': [t],
        'memory': [mem],
        'solution_found': [solution_found],
        'num_cas_served': [num_casualties_served],
        'num_iterations': [num_iterations],
        'accepted_triage': [accepted_triage],
        'initial_limit_vtols': [initial_limit_vtol],
        'primary_sol_primary_obj': [primary_sol_primary_obj],
        'reverse_sol_primary_obj': [reverse_sol_primary_obj],
        'situational_sol_primary_obj': [situational_sol_primary_obj],
        'primary_sol_reverse_obj': [primary_sol_reverse_obj],
        'reverse_sol_reverse_obj': [reverse_sol_reverse_obj],
        'situational_sol_reverse_obj': [situational_sol_reverse_obj],
        'primary_sol_situational_obj': [primary_sol_situational_obj],
        'reverse_sol_situational_obj': [reverse_sol_situational_obj],
        'situational_sol_situational_obj': [situational_sol_situational_obj]


    })

    # Define the CSV file path
    csv_file_path = 'xyz_tp.csv'

    # Append the DataFrame to the CSV file
    if not os.path.isfile(csv_file_path):
        df.to_csv(csv_file_path, index=False)
    else:
        df.to_csv(csv_file_path, mode='a', header=False, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--n_casualties', type=int, default=10, help='number of casualties')
    parser.add_argument('--n_assets', type=int, default=5, help='number of assets')
    parser.add_argument('--n_cfs', type=int, default=10, help='number of care facilities')

    args = parser.parse_args()
    main(args.n_casualties, args.n_assets, args.n_cfs)