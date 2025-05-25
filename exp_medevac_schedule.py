from services.service_medevac_planning.factory.FactoryAlgo import AlgoName, FactoryAlgos
from services.models.ModelConstraints import Constraint
from services.models.ModelSettings import Settings
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility
import json
import pandas as pd
import argparse
def main(n_casualties, n_assets, n_cfs):
    """
    Medical Evacuation (MEDEVAC) Planning Simulation

    This script simulates a medical evacuation planning scenario using predefined datasets for casualties, assets, and care facilities.

    The main function performs the following tasks:
    1. Loads predefined indices for casualties, assets, and care facilities from a CSV file.
    2. Reads JSON files containing data for each casualty, asset, and care facility.
    3. Creates MissionOptionsAssets objects for casualties, Asset objects for assets, and CareFacility objects for care facilities.
    4. Configures settings for the MEDEVAC planning algorithm, including triage algorithms and constraints.
    5. Runs the MEDEVAC planning algorithm to generate urgency-based and reverse triage-based evacuation plans.
    6. Prints the resulting assignments of casualties to assets and care facilities.

    Command-line Arguments:
        --n_casualties (int): Number of casualties to simulate (default: 10)
        --n_assets (int): Number of assets to use (default: 5)
        --n_cfs (int): Number of care facilities to include (default: 1)

    Usage:
        python script_name.py --n_casualties 15 --n_assets 7 --n_cfs 2

    Note:
        This script assumes the existence of a 'indices.csv' file and JSON data files in the 'data' directory.
        The actual MEDEVAC planning algorithm is implemented in the FactoryAlgos class, which is not shown in this script.

    Dependencies:
        - pandas
        - json
        - argparse
        - Custom modules from the 'services' package
    """
    # cas_indexes = random.sample(range(1, 501), n_casualties)
    # assets_indexes = random.sample(range(1, 501), n_assets)
    # cfs_indexes = random.sample(range(1, 101), n_cfs)
    # # Save the indices to a CSV file
    # filename = 'indices.csv'
    #
    # with open(filename, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['casualty_index', 'asset_index', 'cf_index'])
    #
    #     # Write the indices
    #     for i in range(max(len(cas_indexes), len(assets_indexes), len(cfs_indexes))):
    #         casualty = cas_indexes[i] if i < len(cas_indexes) else ''
    #         asset = assets_indexes[i] if i < len(assets_indexes) else ''
    #         cf = cfs_indexes[i] if i < len(cfs_indexes) else ''
    #         writer.writerow([casualty, asset, cf])
    #
    # print(f"Indices saved to {filename}")

    # Read the indices back from the CSV file and ensure they are integers
    df_indices = pd.read_csv("indices.csv")
    cas_indexes = list(df_indices["casualty_index"].dropna().astype(int))
    assets_indexes = list(df_indices["asset_index"].dropna().astype(int))
    cfs_indexes = list(df_indices["cf_index"].dropna().astype(int))

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
            # print(data)
        all_assets.append(
            Asset(asset_name=data['name'], crew_duty_hrs=data['crew_duty_hrs'], asset_range_in_km=data['range_km'],
                  asset_speed_kmph=data['speed_kph'], location=[data['latitude'], data['longitude']]))
        assets_possible.append(data['name'])
    print('Assets loaded.')
    for i in cfs_indexes:
        folder_p = 'data/cf_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        all_care_facilities.append(CareFacility(cf_name=data['name'], location=[data['latitude'], data['longitude']]))
        cfs_possible.append(data['name'])
    print('Care facilties loaded.')
    for i in cas_indexes:
        folder_p = 'data/casualty_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        insults = [key for key in data.keys() if key.startswith('insult')]
        insults_dict = {key: val for key, val in data.items() if key in insults}
        vitals_dict = {
            'gcs': data['gcs'],
            'sbp': data['sbp'],
            'rr': data['rr']
        }
        all_mission_options.append(
            MissionOptionsAssets(patient_name=data['name'], care_facilities_possible=cfs_possible,
                                 assets_possible=assets_possible, insults_dict=insults_dict, vitals_dict=vitals_dict,
                                 location=[data['latitude'], data['longitude']]))
    print('Casualties loaded.')
    settings_test_case = Settings(
        enabled_triage_algos = ['life', 'niss', 'rts'],
        enabled_urgency_opt = True,
        enabled_reverse_opt = True,
        # constraints = [Constraint(constraint_name = 'lsi'), Constraint(constraint_name = 'air_time', constraint_threshold = 3)]
        # constraints = [Constraint(constraint_name='lsi')]
        # constraints=[Constraint(constraint_name='air_time', constraint_threshold=3)]

    )
    algo_mission_assets = FactoryAlgos.create_algo(mode= AlgoName.MEDEVAC_SCHEDULE)
    output_schedule = algo_mission_assets.return_medevac_schedule(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
                                            settings = settings_test_case)
    print('Generated final schedule for medevac operations: ')
    print('(asset name, asset current location, casualty, asset destination location/care facility) ---->  (start timestep, end timestep(hours)')
    for (asset, curr_asset_loc, person, cf), (start_time, end_time) in output_schedule.items():
        print((asset, curr_asset_loc, person, cf), '----> ', (start_time, end_time))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--n_casualties', type=int, default=10, help='number of casualties')
    parser.add_argument('--n_assets', type=int, default=5, help='number of assets')
    parser.add_argument('--n_cfs', type=int, default=1, help='number of care facilities')

    args = parser.parse_args()
    main(args.n_casualties, args.n_assets, args.n_cfs)