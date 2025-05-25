

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


def get_casualties_dicts(missions_options, persons, person_score, person_lsi_ts, person_rtd_ts,
                         person_equipments_needed, all_lats_longs):
    for index, mission in enumerate(missions_options):
        patient_name = mission.patient_name
        patient_triage_score = mission.triage_score
        patient_location = mission.location
        patient_lsi_ts = mission.lsi_ts
        patient_rtd_ts = mission.rtd_ts
        patient_equipments_needed = mission.equipments_needed

        possible_assets = mission.assets_possible
        possible_care_facilities = mission.care_facilities_possible
        persons.append(patient_name)

        person_score[patient_name] = patient_triage_score
        person_lsi_ts[patient_name] = patient_lsi_ts
        person_rtd_ts[patient_name] = patient_rtd_ts
        person_equipments_needed[patient_name] = patient_equipments_needed

        all_lats_longs[patient_name] = patient_location

    return persons, person_score, person_lsi_ts, person_rtd_ts, person_equipments_needed, all_lats_longs


def get_assets_dicts(assets, assets_time_ranges, curr_asset_location,
                     assets_speeds, all_lats_longs, assets_crew_duty_hrs):
    all_assets = []
    for index, asset in enumerate(assets):
        record = asset.specifications_record
        asset_name = record['asset_name']

        asset_range_in_km = record['asset_range_in_km']
        asset_speed_kmph = record['asset_speed_kmph']
        asset_time_range = asset_range_in_km / asset_speed_kmph
        asset_crew_duty_hrs = record['crew_duty_hrs']
        asset_location = record['location']
        all_assets.append(asset_name)
        assets_time_ranges[asset_name] = asset_time_range
        curr_asset_location[asset_name] = asset_name
        assets_speeds[asset_name] = asset_speed_kmph
        all_lats_longs[asset_name] = asset_location
        assets_crew_duty_hrs[asset_name] = asset_crew_duty_hrs

    return all_assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs


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
    required_distance = {}
    required_timesteps_lsi_only = {}
    required_ts_asset_isop = {}
    required_ts_isop_cf = {}

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
                asset_p_dist = haversine_distance(asset_lat, asset_long, person_lat, person_long)
                asset_p_time = asset_p_dist / assets_speeds[asset]
                trip_distance = haversine_distance(asset_lat, asset_long, person_lat,
                                                        person_long) + haversine_distance(person_lat,
                                                                                               person_long, cf_lat,
                                                                                               cf_lon)
                trip_time = trip_distance / assets_speeds[asset]
                required_timesteps[(person, asset, cf)] = trip_time
                required_distance[(person, asset, cf)] = trip_distance
                required_timesteps_lsi_only[(person, asset, cf)] = asset_p_time

                person_cf_d = haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                person_cf_t = person_cf_d / assets_speeds[asset]

                required_ts_asset_isop[(person, asset, cf)] = asset_p_time
                required_ts_isop_cf[(person, asset, cf)] = person_cf_t
    return required_timesteps, required_distance, required_timesteps_lsi_only, required_ts_asset_isop, required_ts_isop_cf
def get_normalized_gcs(gcs):
    if gcs == 3:
        return 0
    if gcs in [4,5]:
        return 1
    if gcs in [6,7,8]:
        return 2
    if gcs in [9,10,11,12]:
        return 3
    if gcs in [13,14,15]:
        return 4
def get_normalized_sbp(sbp):
    if sbp == 0:
        return 0
    if sbp >0 and sbp <49:
        return 1
    if sbp >=49 and sbp < 75:
        return 2
    if sbp >=75 and sbp < 89:
        return 3
    if sbp>=89:
        return 4

def get_normalized_rr(rr):
    if rr == 0:
        return 0
    if rr >0 and rr <5:
        return 1
    if rr >=5 and rr < 9:
        return 2
    if rr >=9 and rr < 29:
        return 4
    if rr>=29:
        return 3
def get_niss_score(insult_dict):
    ais_scores_all = []
    niss_score = 0
    if not insult_dict.keys():
        return None
    for insult, ais in insult_dict.items():
        ais_scores_all.append(ais)
    top_3_ais_scores = sorted(ais_scores_all, reverse=True)[:3]
    for ais_score in top_3_ais_scores:
        niss_score += ais_score*ais_score
    return niss_score
def return_triage_values(insults_dict, vitals_dict):

    insult_ais_scores = []
    gcs = None
    sbp = None
    rr = None
    for insult, ais in insults_dict.items():
        if pd.isna(ais):
            break
        else:
            insult_ais_scores.append(ais)
    for vital, vital_val in vitals_dict.items():
        if pd.isna(vital_val):
            break
        else:
            if vital == 'gcs':
                gcs = vital_val
            elif vital == 'sbp':
                sbp = vital_val
            elif vital == 'rr':
                rr = vital_val

    # Compute scores
    niss_score = None
    rts_score = None
    life_score = None
    if len(insult_ais_scores) > 0:
        niss_score = get_niss_score(insult_dict=insults_dict)
        if niss_score > 75:
            niss_score = 75
        final_score = round(niss_score/75,2)
    if not pd.isna(gcs) and not pd.isna(sbp) and not pd.isna(rr):
        normalized_gcs = get_normalized_gcs(gcs)
        normalized_sbp = get_normalized_sbp(sbp)
        normalized_rr = get_normalized_rr(rr)
        rts_score = normalized_gcs + normalized_sbp + normalized_rr
        final_score = round((12-rts_score)/12,2)

    if not pd.isna(niss_score) and not pd.isna(rts_score):
        life_score = 100 - (round(niss_score/75,2)*50 + round((12-rts_score)/12,2)*50)
        final_score = round(1 - (life_score/100),2)
    triage_category = None
    lsi_hrs = None
    rtd_hrs = None
    resource_required = None
    if final_score <= 0.3:
        triage_category = 'minor'
        lsi_hrs = 24
        rtd_hrs = 12
        resource_required = 1
    elif final_score <= 0.5:
        triage_category = 'delayed'
        lsi_hrs = 4
        rtd_hrs = 360
        resource_required = 2
    elif final_score <= 0.7:
        triage_category = 'urgent'
        lsi_hrs = 2
        rtd_hrs = 1080
        resource_required = 3

    elif final_score > 0.7:
        triage_category = 'immediate'
        lsi_hrs = 1.5
        rtd_hrs = 2160
        resource_required = 4

    return final_score, triage_category, lsi_hrs, rtd_hrs, resource_required

def random_baseline(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_lsi_ts = {}
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
    persons, person_score, person_lsi_ts, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_lsi_ts=person_lsi_ts, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)

    all_assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
        assets_speeds=assets_speeds, all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)

    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps, required_distance, required_timesteps_lsi_only, required_ts_asset_isop, required_ts_isop_cf = get_required_timestamps_dict(
        persons=persons, all_assets=all_assets, all_cfs=all_cfs,
        all_lats_longs=all_lats_longs,
        curr_asset_location=curr_asset_location,
        assets_crew_duty_hrs=assets_crew_duty_hrs,
        assets_speeds=assets_speeds,
        assets_time_ranges=assets_time_ranges)

    # Initialize dictionaries to store assignments and asset availability times
    assignments = {}

    list_persons = persons.copy()
    list_assets = all_assets.copy()

    random.shuffle(list_persons)
    random.shuffle(list_assets)
    list_cfs = all_cfs.copy()

    # remaining_assets = all_assets.copy()
    # remaining_persons = list_persons.copy()

    assignments_status = {}
    # num_iteration = 0
    # terminate = False
    # while not terminate:
    #     num_iteration += 1
    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        if required_timesteps_lsi_only[(chosen_cas, chosen_asset, chosen_cf)] <= person_lsi_ts[chosen_cas]:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # Calculate metrics
    trips_times = []
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    # total_equipment_reqs = []

    # Summarize the results
    for casualty, (asset, care_facility, ts) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        trips_times.append(trip_time)
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                # total_equipment_reqs.append(mission_option.equipments_needed)

    total_triage_score = sum(triage_scores) if triage_scores else 0
    avg_rtd_ts = sum(rtd_tss)/len(rtd_tss) if rtd_tss else None
    avg_trip_time = sum(trips_times)/len(trips_times) if trips_times else None
    # total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0



    return len(served_casualties), avg_trip_time, total_triage_score, avg_rtd_ts


def prioritized_triage_assignment(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_lsi_ts = {}
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
    persons, person_score, person_lsi_ts, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_lsi_ts=person_lsi_ts, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
    all_assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location, assets_speeds=assets_speeds,
        all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)
    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps, required_distance, required_timesteps_lsi_only, required_ts_asset_isop, required_ts_isop_cf = get_required_timestamps_dict(
        persons=persons, all_assets=all_assets, all_cfs=all_cfs,
        all_lats_longs=all_lats_longs,
        curr_asset_location=curr_asset_location,
        assets_crew_duty_hrs=assets_crew_duty_hrs,
        assets_speeds=assets_speeds,
        assets_time_ranges=assets_time_ranges)

    # Initialize dictionaries to store assignments and asset availability times
    assignments = {}

    # list_assets = all_assets.copy()
    # random.shuffle(list_assets)
    list_persons = sorted(persons, key=lambda person: person_score[person], reverse=True)
    list_assets = all_assets.copy()
    random.shuffle(list_assets)
    list_cfs = all_cfs.copy()


    # print(list_assets)
    # print(required_timesteps_lsi_only)
    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        # print(index, chosen_asset, chosen_cf, chosen_cas)
        # print(required_timesteps_lsi_only[(chosen_cas, chosen_asset, chosen_cf)], person_lsi_ts[chosen_cas])
        if required_timesteps_lsi_only[(chosen_cas, chosen_asset, chosen_cf)] <= person_lsi_ts[chosen_cas]:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # Calculate metrics
    trips_times = []
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    # total_equipment_reqs = []

    # Summarize the results
    print(person_lsi_ts)
    print(assignments)
    for casualty, (asset, care_facility, ts) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        trips_times.append(trip_time)
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                # total_equipment_reqs.append(mission_option.equipments_needed)

    total_triage_score = sum(triage_scores) if triage_scores else 0
    avg_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    avg_trip_time = sum(trips_times) / len(trips_times) if trips_times else None
    # total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0

    return len(served_casualties), avg_trip_time, total_triage_score, avg_rtd_ts

def prioritized_rtd_assignment(missions_options, assets, care_facilities):
    persons = []
    all_assets = []
    all_cfs = []

    person_score = {}
    person_lsi_ts = {}
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
    persons, person_score, person_lsi_ts, person_rtd_ts, person_equipments_needed, all_lats_longs = get_casualties_dicts(
        missions_options=missions_options, persons=persons, person_score=person_score,
        person_lsi_ts=person_lsi_ts, person_rtd_ts=person_rtd_ts,
        person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
    all_assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs = get_assets_dicts(
        assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
        assets_speeds=assets_speeds,
        all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)
    all_cfs, all_lats_longs = get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

    required_timesteps, required_distance, required_timesteps_lsi_only, required_ts_asset_isop, required_ts_isop_cf = get_required_timestamps_dict(
        persons=persons, all_assets=all_assets, all_cfs=all_cfs,
        all_lats_longs=all_lats_longs,
        curr_asset_location=curr_asset_location,
        assets_crew_duty_hrs=assets_crew_duty_hrs,
        assets_speeds=assets_speeds,
        assets_time_ranges=assets_time_ranges)

    # Initialize dictionaries to store assignments and asset availability times
    assignments = {}

    list_persons = sorted(persons, key=lambda person: person_rtd_ts[person], reverse=False)
    list_assets = all_assets.copy()
    random.shuffle(list_assets)
    list_cfs = all_cfs.copy()

    # print(list_assets)
    # print(required_timesteps_lsi_only)
    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        # print(index, chosen_asset, chosen_cf, chosen_cas)
        # print(required_timesteps_lsi_only[(chosen_cas, chosen_asset, chosen_cf)], person_lsi_ts[chosen_cas])
        if required_timesteps_lsi_only[(chosen_cas, chosen_asset, chosen_cf)] <= person_lsi_ts[chosen_cas]:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # Calculate metrics
    trips_times = []
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    # total_equipment_reqs = []

    # Summarize the results
    # print(person_lsi_ts)
    # print(assignments)
    for casualty, (asset, care_facility, ts) in assignments.items():
        trip_time = required_timesteps[(casualty, asset, care_facility)]
        trips_times.append(trip_time)
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in missions_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(person_score[served_cas])
                rtd_tss.append(mission_option.rtd_ts)
                # total_equipment_reqs.append(mission_option.equipments_needed)

    total_triage_score = sum(triage_scores) if triage_scores else 0
    avg_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    avg_trip_time = sum(trips_times) / len(trips_times) if trips_times else None
    # total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0

    return len(served_casualties), avg_trip_time, total_triage_score, avg_rtd_ts

def get_required_values(triage_assignments, all_mission_options):
    num_casualties_served = len(triage_assignments.keys())

    # Calculate metrics
    trips_times = []
    total_triage_score = 0
    minimum_rtd_ts = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    for casualty, (asset, cf, trip_time) in triage_assignments.items():
        trips_times.append(trip_time)
        served_casualties.append(casualty)

    for served_cas in served_casualties:
        for mission_option in all_mission_options:
            if mission_option.patient_name == served_cas:
                triage_scores.append(mission_option.triage_score)
                rtd_tss.append(mission_option.rtd_ts)

    total_triage_score = sum(triage_scores) if triage_scores else 0
    avg_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    avg_trip_time = sum(trips_times) / len(trips_times) if trips_times else None
    # total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0

    return len(served_casualties), avg_trip_time, total_triage_score, avg_rtd_ts
def main(n_casualties, n_assets, n_cfs):

    # objectives = ['PRIMARY']
    # objectives = ['REVERSE']
    # objectives = ['SITUATIONAL']

    # Generate random indices

    cas_indexes = random.sample(range(1, 501), n_casualties)
    assets_indexes = random.sample(range(1, 501), n_assets)
    cfs_indexes = random.sample(range(1, 101), n_cfs)
    #
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
    #         writer.writerow([str(int(casualty)) if casualty != '' else '',
    #                          str(int(asset)) if asset != '' else '',
    #                          str(int(cf)) if cf != '' else ''])
    #
    # print(f"Indices saved to {filename}")

    # Read the indices back from the CSV file and ensure they are integers
    # df_indices = pd.read_csv("indices.csv")
    # cas_indexes = list(df_indices["casualty_index"].dropna().astype(int))
    # assets_indexes = list(df_indices["asset_index"].dropna().astype(int))
    # cfs_indexes = list(df_indices["cf_index"].dropna().astype(int))

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
        all_assets.append(Asset(asset_name=data['name'], crew_duty_hrs=data['crew_duty_hrs'], asset_range_in_km=data['range_km'], asset_speed_kmph=data['speed_kph'], location=[data['latitude'], data['longitude']]))
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
        insults = [key for key in data.keys() if key.startswith('insult')]
        insults_dict = {key: val for key, val in data.items() if key in insults}
        vitals_dict = {
            'gcs': data['gcs'],
            'sbp': data['sbp'],
            'rr': data['rr']
        }
        all_mission_options.append(
            MissionOptionsAssets(patient_name=data['name'], care_facilities_possible=cfs_possible,
                                 assets_possible=assets_possible, insults_dict = insults_dict, vitals_dict = vitals_dict,
                                 location=[data['latitude'], data['longitude']]))


    algo_mission_assets = FactoryAlgos.create_algo(mode=AlgoName.SINGLE_OBJ)
    mission_final_assets_primary, solution_found_primary, assignment_final_primary, all_persons_primary, person_scores_primary, person_lsi_ts_primary, person_rtd_ts_primary, person_equipments_needed_primary, req_ts_primary, updated_missions_options_primary = algo_mission_assets.return_final_assignments_single_obj(
        missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
        objectives=['PRIMARY'])

    mission_final_assets_reverse, solution_found_reverse, assignment_final_reverse, all_persons_reverse, person_scores_reverse, person_lsi_ts_reverse, person_rtd_ts_reverse, person_equipments_needed_reverse, req_ts_reverse, updated_missions_options_reverse = algo_mission_assets.return_final_assignments_single_obj(
        missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
        objectives=['REVERSE'])

    mission_final_assets_situational, solution_found_situational, assignment_final_situational, all_persons_situational, person_scores_situational, person_lsi_ts_situational, person_rtd_ts_situational, person_equipments_needed_situational, req_ts_situational, updated_missions_options_situational = algo_mission_assets.return_final_assignments_single_obj(
        missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
        objectives=['SITUATIONAL'])




    num_cas_served_primary, avg_trip_time_primary, total_triage_score_primary, avg_rtd_ts_primary = get_required_values(triage_assignments=assignment_final_primary, all_mission_options=updated_missions_options_primary)
    num_cas_served_reverse, avg_trip_time_reverse, total_triage_score_reverse, avg_rtd_ts_reverse = get_required_values(triage_assignments=assignment_final_reverse, all_mission_options=updated_missions_options_reverse)
    num_cas_served_situational, avg_trip_time_situational, total_triage_score_situational, avg_rtd_ts_situational = get_required_values(triage_assignments=assignment_final_situational, all_mission_options=updated_missions_options_situational)


    # GEt metrics for random baseline
    num_cas_served_random, avg_trip_time_random, total_triage_score_random, avg_rtd_ts_random = random_baseline(missions_options=updated_missions_options_reverse, assets=all_assets, care_facilities=all_care_facilities)
    num_cas_served_triage, avg_trip_time_triage, total_triage_score_triage, avg_rtd_ts_triage = prioritized_triage_assignment(missions_options=updated_missions_options_reverse, assets=all_assets, care_facilities=all_care_facilities)
    num_cas_served_rtd, avg_trip_time_rtd, total_triage_score_rtd, avg_rtd_ts_rtd = prioritized_rtd_assignment(missions_options=updated_missions_options_reverse, assets=all_assets, care_facilities=all_care_facilities)


    # Create a DataFrame with the required data
    df = pd.DataFrame({
        'num_cas': [n_casualties],
        'num_assets': [n_assets],
        'solution_found_primary': [solution_found_primary],
        'num_cas_served_primary': [num_cas_served_primary],
        'avg_trips_time_primary': [avg_trip_time_primary],
        'total_triage_score_primary':[total_triage_score_primary],
        'avg_rtd_ts_primary': [avg_rtd_ts_primary],
        'solution_found_reverse': [solution_found_reverse],
        'num_cas_served_reverse': [num_cas_served_reverse],
        'avg_trips_time_reverse': [avg_trip_time_reverse],
        'total_triage_score_reverse': [total_triage_score_reverse],
        'avg_rtd_ts_reverse': [avg_rtd_ts_reverse],
        'solution_found_situational': [solution_found_situational],
        'num_cas_served_situational': [num_cas_served_situational],
        'avg_trips_time_situational': [avg_trip_time_situational],
        'total_triage_score_situational': [total_triage_score_situational],
        'avg_rtd_ts_situational': [avg_rtd_ts_situational],

        'num_cas_served_random': [num_cas_served_random],
        'avg_trips_time_random': [avg_trip_time_random],
        'total_triage_score_random': [total_triage_score_random],
        'avg_rtd_ts_random': [avg_rtd_ts_random],
        'num_cas_served_triage': [num_cas_served_triage],
        'avg_trips_time_triage': [avg_trip_time_triage],
        'total_triage_score_triage': [total_triage_score_triage],
        'avg_rtd_ts_triage': [avg_rtd_ts_triage],
        'num_cas_served_rtd': [num_cas_served_rtd],
        'avg_trips_time_rtd': [avg_trip_time_rtd],
        'total_triage_score_rtd': [total_triage_score_rtd],
        'avg_rtd_ts_rtd': [avg_rtd_ts_rtd],


    })

    # Define the directory and file path
    directory = 'baseline_individual_tables'
    csv_file_path = os.path.join(directory, 'experiment_baseline_single_obj.csv')

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Append the DataFrame to the CSV file
    if not os.path.isfile(csv_file_path):
        df.to_csv(csv_file_path, index=False)
    else:
        df.to_csv(csv_file_path, mode='a', header=False, index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--n_casualties', type=int, default=25, help='number of casualties')
    parser.add_argument('--n_assets', type=int, default=10, help='number of assets')
    parser.add_argument('--n_cfs', type=int, default=1, help='number of care facilities')

    args = parser.parse_args()
    main(args.n_casualties, args.n_assets, args.n_cfs)