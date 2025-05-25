

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


def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers
    r = 6371

    # Calculate the result
    return c * r


def travel_time(lat1, lon1, lat2, lon2, speed):
    # Calculate the distance using the Haversine formula
    distance = haversine_distance(lat1, lon1, lat2, lon2)

    # Calculate the time in hours
    time_hours = distance / speed

    # Convert time to minutes
    # time_minutes = time_hours * 60
    # time_minutes = int(math.ceil(time_minutes))

    return time_hours


def get_casualties_dicts(missions_options, persons, person_score, person_ts_available, person_rtd_ts,
                         person_equipments_needed, all_lats_longs):
    for index, mission in enumerate(missions_options):
        patient_name = mission.patient_name
        patient_triage_score = mission.triage_score
        patient_location = mission.location
        patient_ts_available = mission.available_ts
        patient_rtd_ts = mission.rtd_ts
        patient_equipments_needed = mission.equipments_needed

        possible_assets = mission.assets_possible
        possible_care_facilities = mission.care_facilities_possible
        persons.append(patient_name)

        person_score[patient_name] = 1 - (patient_triage_score / 100)
        person_ts_available[patient_name] = patient_ts_available
        person_rtd_ts[patient_name] = patient_rtd_ts
        person_equipments_needed[patient_name] = patient_equipments_needed

        all_lats_longs[patient_name] = patient_location

    return persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs


def get_assets_dicts(assets, assets_time_ranges, curr_asset_location, asset_vtol_dict, asset_ground_dict,
                     assets_speeds, all_lats_longs, assets_crew_duty_hrs):
    all_assets = []
    for index, asset in enumerate(assets):
        record = asset.specifications_record
        asset_name = record['asset_name']
        asset_ground = record['asset_ground']
        asset_vtol = record['asset_vtol']
        asset_range_in_km = record['asset_range_in_km']
        asset_speed_kmph = record['asset_speed_kmph']
        asset_time_range = asset_range_in_km / asset_speed_kmph
        asset_crew_duty_hrs = record['crew_duty_hrs']
        asset_location = record['location']
        all_assets.append(asset_name)
        assets_time_ranges[asset_name] = asset_time_range
        curr_asset_location[asset_name] = asset_name
        asset_vtol_dict[asset_name] = asset_vtol
        asset_ground_dict[asset_name] = asset_ground
        assets_speeds[asset_name] = asset_speed_kmph
        all_lats_longs[asset_name] = asset_location
        assets_crew_duty_hrs[asset_name] = asset_crew_duty_hrs

    return all_assets, assets_time_ranges, curr_asset_location, asset_vtol_dict, asset_ground_dict, assets_speeds, all_lats_longs, assets_crew_duty_hrs


def get_cf_dicts(care_facilities, all_lats_longs):
    all_cfs = []
    for index, cf in enumerate(care_facilities):
        record = cf.specifications_record
        cf_name = record['cf_name']
        cf_location = record['location']
        all_cfs.append(cf_name)
        all_lats_longs[cf_name] = cf_location
    return all_cfs, all_lats_longs


def get_required_timestamps_dict(persons, all_assets, all_cfs, all_lats_longs, curr_asset_location,
                                 assets_crew_duty_hrs, assets_speeds, assets_time_ranges):
    required_timesteps = {}
    for person in persons:
        person_lat = all_lats_longs[person][0]
        person_long = all_lats_longs[person][1]
        for asset in all_assets:
            source_location = curr_asset_location[asset]
            asset_lat = all_lats_longs[source_location][0]
            asset_long = all_lats_longs[source_location][1]
            crew_duty_hrs = assets_crew_duty_hrs[asset]
            for cf in all_cfs:
                cf_lat = all_lats_longs[cf][0]
                cf_lon = all_lats_longs[cf][1]
                trip_distance = haversine_distance(asset_lat, asset_long, person_lat,
                                                        person_long) + haversine_distance(person_lat, person_long,
                                                                                               cf_lat, cf_lon)
                trip_time = trip_distance / assets_speeds[asset]

                if trip_time <= assets_time_ranges[asset] and trip_time < crew_duty_hrs:
                    required_timesteps[(person, asset, cf)] = trip_time
    return required_timesteps


def random_baseline(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_ts_available = {}
    person_rtd_ts = {}
    person_equipments_needed = {}
    required_timesteps = {}
    curr_asset_location = {}
    all_lats_longs = {}
    asset_ground_dict = {}
    asset_vtol_dict = {}
    assets_speeds = {}
    assets_time_ranges = {}
    assets_crew_duty_hrs = {}

    # Initialize dictionaries and lists
    persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_ts_available=person_ts_available, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)

    all_assets, assets_time_ranges, curr_asset_location, asset_vtol_dict, asset_ground_dict, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
        asset_vtol_dict=asset_vtol_dict, asset_ground_dict=asset_ground_dict, assets_speeds=assets_speeds,
        all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)

    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps = get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                      all_lats_longs=all_lats_longs,
                                                      curr_asset_location=curr_asset_location,
                                                      assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                      assets_speeds=assets_speeds,
                                                      assets_time_ranges=assets_time_ranges)

    print(persons)
    print(all_assets)
    print(all_cfs)
    print(required_timesteps)

    # Initialize dictionaries to store assignments and asset availability times
    assignments = {}
    asset_availability = {asset: 0 for asset in all_assets}

    # Copy lists to avoid modifying the original lists
    remaining_persons = persons.copy()

    # Assign assets to casualties iteratively
    while remaining_persons:
        assigned_this_round = []
        for casualty in remaining_persons:
            valid_assignments = [(asset, cf) for asset in all_assets for cf in all_cfs if
                                 (casualty, asset, cf) in required_timesteps and
                                 required_timesteps[(casualty, asset, cf)] + asset_availability[asset] <=
                                 assets_time_ranges[asset]]

            if valid_assignments:
                # Randomly select a valid (asset, cf) pair
                asset, care_facility = random.choice(valid_assignments)
                assignments[casualty] = (asset, care_facility)

                # Update the asset's availability time
                trip_time = required_timesteps[(casualty, asset, care_facility)]
                asset_availability[asset] += trip_time

                # Mark this casualty as assigned
                assigned_this_round.append(casualty)

        # Remove assigned casualties from the list of remaining persons
        for casualty in assigned_this_round:
            remaining_persons.remove(casualty)

        # If no assignments were made in this round, break the loop to avoid infinite looping
        if not assigned_this_round:
            break

    # Calculate metrics
    total_trips_time = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Summarize the results
    for casualty, (asset, care_facility) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        total_trips_time += trip_time
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                total_equipment_reqs.append(mission_option.equipments_needed)

    average_triage_score = sum(triage_scores) / len(triage_scores) if triage_scores else 0
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else 0
    total_equipment_req = sum(total_equipment_reqs)

    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req


def prioritized_triage_assignment(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_ts_available = {}
    person_rtd_ts = {}
    person_equipments_needed = {}
    required_timesteps = {}
    curr_asset_location = {}
    all_lats_longs = {}
    asset_ground_dict = {}
    asset_vtol_dict = {}
    assets_speeds = {}
    assets_time_ranges = {}
    assets_crew_duty_hrs = {}

    # Get all the necessary data
    persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_ts_available=person_ts_available, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
    all_assets, assets_time_ranges, curr_asset_location, asset_vtol_dict, asset_ground_dict, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
        asset_vtol_dict=asset_vtol_dict, asset_ground_dict=asset_ground_dict, assets_speeds=assets_speeds,
        all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)
    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps = get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                      all_lats_longs=all_lats_longs,
                                                      curr_asset_location=curr_asset_location,
                                                      assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                      assets_speeds=assets_speeds,
                                                      assets_time_ranges=assets_time_ranges)

    # Initialize empty dictionary to store assignments
    assignments = {}

    # Copy lists to avoid modifying the original lists
    remaining_assets = all_assets.copy()

    # Sort casualties based on their scores in descending order
    sorted_persons = sorted(persons, key=lambda x: person_score[x], reverse=True)

    # Assign the highest score casualties first to the asset-care facility pair with the least timesteps
    for casualty in sorted_persons:
        valid_assignments = [(asset, cf) for asset in remaining_assets for cf in all_cfs if
                             (casualty, asset, cf) in required_timesteps]

        if valid_assignments:
            # Find the (asset, cf) pair with the least required timesteps
            asset, care_facility = min(valid_assignments, key=lambda x: required_timesteps[(casualty, x[0], x[1])])
            assignments[casualty] = (asset, care_facility)

            # Remove the assigned asset from the remaining list to ensure it's used only once
            remaining_assets.remove(asset)
        else:
            # If no valid assignment exists, we can't assign this casualty
            print(f"No valid assignment for {casualty}")

    total_trips_time = 0
    average_triage_score = 0
    average_rtd_ts = 0
    total_equipment_req = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Calculate the total trip time and other metrics
    for casualty, (asset, care_facility) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        total_trips_time += trip_time

    for casualty, (asset, cf) in assignments.items():
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                total_equipment_reqs.append(mission_option.equipments_needed)

    average_triage_score = sum(triage_scores) / len(triage_scores)
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss)
    total_equipment_req = sum(total_equipment_reqs)
    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req

def prioritized_rtd_assignment(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_ts_available = {}
    person_rtd_ts = {}
    person_equipments_needed = {}
    required_timesteps = {}
    curr_asset_location = {}
    all_lats_longs = {}
    asset_ground_dict = {}
    asset_vtol_dict = {}
    assets_speeds = {}
    assets_time_ranges = {}
    assets_crew_duty_hrs = {}

    # Get all the necessary data
    persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_ts_available=person_ts_available, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
    all_assets, assets_time_ranges, curr_asset_location, asset_vtol_dict, asset_ground_dict, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
        asset_vtol_dict=asset_vtol_dict, asset_ground_dict=asset_ground_dict, assets_speeds=assets_speeds,
        all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)
    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps = get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                      all_lats_longs=all_lats_longs,
                                                      curr_asset_location=curr_asset_location,
                                                      assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                      assets_speeds=assets_speeds,
                                                      assets_time_ranges=assets_time_ranges)

    # Initialize empty dictionary to store assignments
    assignments = {}

    # Copy lists to avoid modifying the original lists
    remaining_assets = all_assets.copy()

    # Sort casualties based on their scores in descending order
    sorted_persons = sorted(persons, key=lambda x: person_rtd_ts[x], reverse=False)

    # Assign the highest score casualties first to the asset-care facility pair with the least timesteps
    for casualty in sorted_persons:
        valid_assignments = [(asset, cf) for asset in remaining_assets for cf in all_cfs if
                             (casualty, asset, cf) in required_timesteps]

        if valid_assignments:
            # Find the (asset, cf) pair with the least required timesteps
            asset, care_facility = min(valid_assignments, key=lambda x: required_timesteps[(casualty, x[0], x[1])])
            assignments[casualty] = (asset, care_facility)

            # Remove the assigned asset from the remaining list to ensure it's used only once
            remaining_assets.remove(asset)
        else:
            # If no valid assignment exists, we can't assign this casualty
            print(f"No valid assignment for {casualty}")

    total_trips_time = 0
    average_triage_score = 0
    average_rtd_ts = 0
    total_equipment_req = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Calculate the total trip time and other metrics
    for casualty, (asset, care_facility) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        total_trips_time += trip_time

    for casualty, (asset, cf) in assignments.items():
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                total_equipment_reqs.append(mission_option.equipments_needed)

    average_triage_score = sum(triage_scores) / len(triage_scores)
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss)
    total_equipment_req = sum(total_equipment_reqs)
    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req

def prioritized_equipments_assignment(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_ts_available = {}
    person_rtd_ts = {}
    person_equipments_needed = {}
    required_timesteps = {}
    curr_asset_location = {}
    all_lats_longs = {}
    asset_ground_dict = {}
    asset_vtol_dict = {}
    assets_speeds = {}
    assets_time_ranges = {}
    assets_crew_duty_hrs = {}

    # Get all the necessary data
    persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_ts_available=person_ts_available, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
    all_assets, assets_time_ranges, curr_asset_location, asset_vtol_dict, asset_ground_dict, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
        asset_vtol_dict=asset_vtol_dict, asset_ground_dict=asset_ground_dict, assets_speeds=assets_speeds,
        all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)
    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps = get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                      all_lats_longs=all_lats_longs,
                                                      curr_asset_location=curr_asset_location,
                                                      assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                      assets_speeds=assets_speeds,
                                                      assets_time_ranges=assets_time_ranges)

    # Initialize empty dictionary to store assignments
    assignments = {}

    # Copy lists to avoid modifying the original lists
    remaining_assets = all_assets.copy()

    # Sort casualties based on their scores in descending order
    sorted_persons = sorted(persons, key=lambda x: person_equipments_needed[x], reverse=True)

    # Assign the highest score casualties first to the asset-care facility pair with the least timesteps
    for casualty in sorted_persons:
        valid_assignments = [(asset, cf) for asset in remaining_assets for cf in all_cfs if
                             (casualty, asset, cf) in required_timesteps]

        if valid_assignments:
            # Find the (asset, cf) pair with the least required timesteps
            asset, care_facility = min(valid_assignments, key=lambda x: required_timesteps[(casualty, x[0], x[1])])
            assignments[casualty] = (asset, care_facility)

            # Remove the assigned asset from the remaining list to ensure it's used only once
            remaining_assets.remove(asset)
        else:
            # If no valid assignment exists, we can't assign this casualty
            print(f"No valid assignment for {casualty}")

    total_trips_time = 0
    average_triage_score = 0
    average_rtd_ts = 0
    total_equipment_req = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Calculate the total trip time and other metrics
    for casualty, (asset, care_facility) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        total_trips_time += trip_time

    for casualty, (asset, cf) in assignments.items():
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                total_equipment_reqs.append(mission_option.equipments_needed)

    average_triage_score = sum(triage_scores) / len(triage_scores)
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss)
    total_equipment_req = sum(total_equipment_reqs)
    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req

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

    # Generate random indices
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
            writer.writerow([str(int(casualty)) if casualty != '' else '',
                             str(int(asset)) if asset != '' else '',
                             str(int(cf)) if cf != '' else ''])

    print(f"Indices saved to {filename}")

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

    print('Assets')
    for i in assets_indexes:
        folder_p = 'data/asset_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        all_assets.append(Asset(asset_name=data['name'], asset_ground=data['ground'], asset_vtol=data['vtol'],
                                crew_duty_hrs=data['crew_duty_hrs'], asset_range_in_km=data['range_km'],
                                asset_speed_kmph=data['speed_kph'], location=[data['latitude'], data['longitude']]))
        assets_possible.append(data['name'])
    print('Care facilties')
    for i in cfs_indexes:
        folder_p = 'data/cf_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        all_care_facilities.append(CareFacility(cf_name=data['name'], location=[data['latitude'], data['longitude']]))
        cfs_possible.append(data['name'])
    print('Casualties')
    for i in cas_indexes:
        folder_p = 'data/casualty_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        all_mission_options.append(
            MissionOptionsAssets(patient_name=data['name'], care_facilities_possible=cfs_possible,
                                 assets_possible=assets_possible, triage_score=data['triage_score'],
                                 rtd_ts=data['rtd_ts'], equipments_needed=data['equipments_needed'],
                                 location=[data['latitude'], data['longitude']]))


    algo_mission_assets = FactoryAlgos.create_algo(mode=AlgoName.MULTIPLE_OBJ)
    (assets_all_missions, num_iterations, accepted_triage, initial_limit_vtol, assignment_final, (assignment_primary, assignment_reverse, assignment_situational),
     (primary_sol_primary_obj, reverse_sol_primary_obj, situational_sol_primary_obj),
     (primary_sol_reverse_obj, reverse_sol_reverse_obj, situational_sol_reverse_obj),
     (primary_sol_situational_obj, reverse_sol_situational_obj,
      situational_sol_situational_obj)) = algo_mission_assets.return_final_assignments_multiple_obj(
        missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
        objectives=['PRIMARY', 'REVERSE', 'SITUATIONAL'],
        constraints={'vtol': math.ceil(len(all_assets) / 2)})
    if len(assets_all_missions) > 0:
        solution_found = 1
    else:
        solution_found = 0


    num_cas_served_primary, total_trips_time_primary, average_triage_score_primary, average_rtd_ts_primary, total_equipment_req_primary = get_required_values(triage_assignments=assignment_primary, all_mission_options=all_mission_options)
    num_cas_served_reverse, total_trips_time_reverse, average_triage_score_reverse, average_rtd_ts_reverse, total_equipment_req_reverse = get_required_values(triage_assignments=assignment_reverse, all_mission_options=all_mission_options)
    num_cas_served_situational, total_trips_time_situational, average_triage_score_situational, average_rtd_ts_situational, total_equipment_req_situational = get_required_values(triage_assignments=assignment_situational, all_mission_options=all_mission_options)


    # GEt metrics for random baseline
    num_served_cas_random, total_trips_time_random, average_triage_score_random, average_rtd_ts_random, total_equipment_req_random = random_baseline(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    num_served_triage, total_trips_time_triage, average_triage_score_triage, average_rtd_ts_triage, total_equipment_req_triage = prioritized_triage_assignment(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    num_served_rtd, total_trips_time_rtd, average_triage_score_rtd, average_rtd_ts_rtd, total_equipment_req_rtd = prioritized_rtd_assignment(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    num_served_equipments, total_trips_time_equipments, average_triage_score_equipments, average_rtd_ts_equipments, total_equipment_req_equipments = prioritized_equipments_assignment(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)


    # Create a DataFrame with the required data
    df = pd.DataFrame({
        'num_cas': [n_casualties],
        'num_assets': [n_assets],
        'solution_found_milp': [solution_found],
        'accepted_triage_milp': [accepted_triage],
        'num_cas_served_primary': [num_cas_served_primary],
        'total_trips_time_primary': [total_trips_time_primary],
        'average_triage_score_primary': [average_triage_score_primary],
        'average_rtd_time_primary': [average_rtd_ts_primary],
        'total_equipment_req_primary': [total_equipment_req_primary],
        'num_cas_served_reverse': [num_cas_served_reverse],
        'total_trips_time_reverse': [total_trips_time_reverse],
        'average_triage_score_reverse': [average_triage_score_reverse],
        'average_rtd_time_reverse': [average_rtd_ts_reverse],
        'total_equipment_req_reverse': [total_equipment_req_reverse],
        'num_cas_served_situational': [num_cas_served_situational],
        'total_trips_time_situational': [total_trips_time_situational],
        'average_triage_score_situational': [average_triage_score_situational],
        'average_rtd_time_situational': [average_rtd_ts_situational],
        'total_equipment_req_situational': [total_equipment_req_situational],
        'num_cas_served_random': [num_served_cas_random],
        'num_cas_served_triage': [num_served_triage],
        'num_cas_served_equipment': [num_served_equipments],
        'num_cas_served_rtd': [num_served_rtd],
        'total_trips_time_random': [total_trips_time_random],
        'total_trips_time_triage': [total_trips_time_triage],
        'total_trips_time_rtd': [total_trips_time_rtd],
        'total_trips_time_equipment': [total_trips_time_equipments],
        'average_triage_score_random': [average_triage_score_random],
        'average_triage_score_triage': [average_triage_score_triage],
        'average_triage_score_rtd': [average_triage_score_rtd],
        'average_triage_score_equipment': [average_triage_score_equipments],
        'average_rtd_time_random': [average_rtd_ts_random],
        'average_rtd_time_triage': [average_rtd_ts_triage],
        'average_rtd_time_rtd': [average_rtd_ts_rtd],
        'average_rtd_time_equipment': [average_rtd_ts_equipments],
        'total_equipment_req_random': [total_equipment_req_random],
        'total_equipment_req_triage': [total_equipment_req_triage],
        'total_equipment_req_rtd': [total_equipment_req_rtd],
        'total_equipment_req_equipment': [total_equipment_req_equipments]


    })


    # Define the CSV file path
    csv_file_path = 'experiment_baseline_3.csv'

    # Append the DataFrame to the CSV file
    if not os.path.isfile(csv_file_path):
        df.to_csv(csv_file_path, index=False)
    else:
        df.to_csv(csv_file_path, mode='a', header=False, index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--n_casualties', type=int, default=25, help='number of casualties')
    parser.add_argument('--n_assets', type=int, default=15, help='number of assets')
    parser.add_argument('--n_cfs', type=int, default=10, help='number of care facilities')

    args = parser.parse_args()
    main(args.n_casualties, args.n_assets, args.n_cfs)