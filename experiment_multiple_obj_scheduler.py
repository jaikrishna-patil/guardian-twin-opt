

from services.service_optimization.factory.FactoryAlgo import AlgoName, FactoryAlgos
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
import math
import csv
def get_required_values(triage_assignments, all_mission_options):
    num_casualties_served = len(triage_assignments.keys())

    total_trips_time = 0
    average_triage_score = 0
    average_rtd_ts = 0
    total_equipment_req = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    for casualty, (asset, cf, trip_time) in triage_assignments.items():
        served_casualties.append(casualty)
        total_trips_time += trip_time

    for served_cas in served_casualties:
        for mission_option in all_mission_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(1 - (mission_option.triage_score / 100))
                rtd_tss.append(mission_option.rtd_ts)
                total_equipment_reqs.append(mission_option.equipments_needed)
    average_triage_score = sum(triage_scores) / len(triage_scores)
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss)
    total_equipment_req = sum(total_equipment_reqs)
    return num_casualties_served, total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req
def main(n_casualties, n_assets, n_cfs):


    cas_indexes = random.sample(range(1, 501), n_casualties)
    assets_indexes = random.sample(range(1, 501), n_assets)
    cfs_indexes = random.sample(range(1, 101), n_cfs)
    # Save the indices to a CSV file
    filename = 'indices.csv'

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['casualty_index', 'asset_index', 'cf_index'])

        # Write the indices
        for i in range(max(len(cas_indexes), len(assets_indexes), len(cfs_indexes))):
            casualty = cas_indexes[i] if i < len(cas_indexes) else ''
            asset = assets_indexes[i] if i < len(assets_indexes) else ''
            cf = cfs_indexes[i] if i < len(cfs_indexes) else ''
            writer.writerow([casualty, asset, cf])

    print(f"Indices saved to {filename}")

    # cas_indexes = [100,10,20,30,40,50,60,70,80,90]
    # assets_indexes = [1,5,10,15,20,25]
    # cfs_indexes = [1,5,10,15,20,25,30,35,40,50]
    # cas_indexes = [103, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    # assets_indexes = [11, 5, 10, 15, 20]
    # cfs_indexes = [1, 5, 10, 15, 20, 29, 30, 35, 37, 50]
    assets_possible = []
    cfs_possible = []
    all_mission_options = []
    all_assets = []
    all_care_facilities = []

    print('Assets')
    for i in assets_indexes:
        folder_p = 'data/asset_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            print(data)
        all_assets.append(Asset(asset_name=data['name'], asset_ground=data['ground'], asset_vtol=data['vtol'], crew_duty_hrs = data['crew_duty_hrs'], asset_range_in_km= data['range_km'], asset_speed_kmph=data['speed_kph'], location=[data['latitude'], data['longitude']]))
        assets_possible.append(data['name'])
    print('Care facilties')
    for i in cfs_indexes:
        folder_p = 'data/cf_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            print(data)
        all_care_facilities.append(CareFacility(cf_name=data['name'], location=[data['latitude'], data['longitude']]))
        cfs_possible.append(data['name'])
    print('Casualties')
    for i in cas_indexes:
        folder_p = 'data/casualty_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            print(data)
        all_mission_options.append(MissionOptionsAssets(patient_name=data['name'], care_facilities_possible=cfs_possible, assets_possible=assets_possible, triage_score=data['triage_score'], rtd_ts= data['rtd_ts'], equipments_needed = data['equipments_needed'],
                                                        location=[data['latitude'], data['longitude']]))

    # print("")
    # print("ALGO :: Mission options assets -> Mission final asset")
    algo_mission_assets = FactoryAlgos.create_algo(mode= AlgoName.MULTIPLE_OBJ_SCHEDULER)
    start = time.time()
    tracemalloc.start()
    assets_all_missions, num_iterations, accepted_triage, schedule_dict  = algo_mission_assets.return_final_assignments_multiple_obj_scheduler(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
                                                                                                                                                              objectives = ['PRIMARY', 'REVERSE', 'SITUATIONAL'])

    if len(schedule_dict.keys()) > 0:
        solution_found = 1
    else:
        solution_found = 0
    num_casualties_served = len(schedule_dict.keys())

    print(schedule_dict)
    # Create a DataFrame with the required data
    df = pd.DataFrame({
        'num_cas': [n_casualties],
        'num_assets': [n_assets],
        'solution_found': [solution_found],
        'num_cas_served': [num_casualties_served],
        'num_iterations': [num_iterations],
        'accepted_triage': [accepted_triage]


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