

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
                    required_distance[(person, asset, cf)] = trip_distance
    return required_timesteps, required_distance
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
    if sbp >=1 and sbp <49:
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
    if rr >=1 and rr <5:
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
    if final_score <= 0.5:
        triage_category = 'minor'
        lsi_hrs = 24
        rtd_hrs = 12
        resource_required = 1
    elif final_score <= 0.8:
        triage_category = 'urgent'
        lsi_hrs = 2
        rtd_hrs = 1080
        resource_required = 2
    elif final_score >0.8:
        triage_category = 'immediate'
        lsi_hrs = 1.5
        rtd_hrs = 2160
        resource_required = 3

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

    required_timesteps, req_distance = get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
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

    assignments_status = {}
    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        if (chosen_cas, chosen_asset, chosen_cf) in required_timesteps:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # temp_req_ts = required_timesteps.copy()
    # for person in list_persons:
    #     all_possible_ass_cf = []
    #     for (cas, ass, cf) in temp_req_ts.keys():
    #         if cas == person:
    #             all_possible_ass_cf.append((ass, cf))
    #
    #     if all_possible_ass_cf:
    #         (chosen_ass, chosen_cf) = random.choice(all_possible_ass_cf)
    #         assignments[person] = (chosen_ass, chosen_cf, temp_req_ts[(person, chosen_ass, chosen_cf)])
    #         # Create a list of keys to delete
    #         keys_to_delete = []
    #         for (cas, ass, cf) in temp_req_ts.keys():
    #             if ass == chosen_ass:
    #                 keys_to_delete.append((cas, ass, cf))
    #
    #         # Delete keys after iteration
    #         for key in keys_to_delete:
    #             del temp_req_ts[key]







    # Calculate metrics
    total_trips_time = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Summarize the results
    for casualty, (asset, care_facility, ts) in assignments.items():
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
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0

    for index, mission in enumerate(missions_options):
        insults_dict = mission.insults_dict
        vitals_dict = mission.vitals_dict
        triage_score, triage_category, lsi_ts, rtd_ts, equipments_needed = return_triage_values(
            insults_dict=insults_dict, vitals_dict=vitals_dict)
        mission.triage_score = triage_score
        mission.triage_category = triage_category
        mission.lsi_ts = lsi_ts
        mission.rtd_ts = rtd_ts
        mission.equipments_needed = equipments_needed


    assignment_final = assignments.copy()
    columns = [
        'Isolated Casualty', 'Assigned MEDEVAC Asset', 'Assigned Care facility',
        'Route Distance (km)', 'Average Speed (km/hr)', 'Available Range',
        'Roundtrip Time (min)', 'Crew Hours Remaining',
        'Medical Triage Category', 'Medical Triage Score', 'Need Life Saving Intervention in: (min)',
        'Forecasted Survival Status', 'Return to Duty in: (days)',
        'Resource Requirement'
    ]
    df = pd.DataFrame(columns=columns)
    for person in persons:
        assigned_asset = None
        assigned_cf = None
        roundtrip_time_min = None
        roundtrip_distance_km = None
        average_speed_kmph = None
        available_range_km = None
        crew_hrs_remaining = None
        triage_category = None
        triage_score = None
        lsi = None
        rtd = None
        resource = None
        survival_status = None

        for mission in missions_options:
            if mission.patient_name == person:
                triage_category = mission.triage_category
                triage_score = mission.triage_score
                lsi = round(mission.lsi_ts * 60, 2)
                rtd = round(mission.rtd_ts / 24, 2)
                resource = mission.equipments_needed

        if person in assignment_final.keys():
            survival_status = 1
            assigned_asset = assignment_final[person][0]
            assigned_cf = assignment_final[person][1]
            roundtrip_time_min = round(assignment_final[person][2] * 60, 2)
            roundtrip_distance_km = round(req_distance[(person, assigned_asset, assigned_cf)], 2)

            for asset in assets:
                asset_record = asset.specifications_record
                if asset_record['asset_name'] == assigned_asset:
                    average_speed_kmph = asset_record['asset_speed_kmph']
                    available_range_km = asset_record['asset_range_in_km']
                    crew_hrs_remaining = asset_record['crew_duty_hrs']
        else:
            survival_status = 0

        row1 = pd.DataFrame([{
            'Isolated Casualty': person,
            'Assigned MEDEVAC Asset': assigned_asset,
            'Assigned Care facility': assigned_cf,
            'Route Distance (km)': roundtrip_distance_km,
            'Average Speed (km/hr)': average_speed_kmph,
            'Available Range': available_range_km,
            'Roundtrip Time (min)': roundtrip_time_min,
            'Crew Hours Remaining': crew_hrs_remaining,
            'Medical Triage Category': triage_category,
            'Medical Triage Score': triage_score,
            'Need Life Saving Intervention in: (min)': lsi,
            'Forecasted Survival Status': survival_status,
            'Return to Duty in: (days)': rtd,
            'Resource Requirement': resource
        }])
        df = pd.concat([df, row1], ignore_index=True)
    print(df)
    print(assignment_final)
    # # Define the CSV file path
    csv_file_path = f'sample_single_obj_random.csv'

    # Append the DataFrame to the CSV file
    df.to_csv(csv_file_path, mode='w', header=True, index=True)


    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req


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

    required_timesteps, req_distance = get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                      all_lats_longs=all_lats_longs,
                                                      curr_asset_location=curr_asset_location,
                                                      assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                      assets_speeds=assets_speeds,
                                                      assets_time_ranges=assets_time_ranges)

    # Initialize dictionaries to store assignments and asset availability times
    assignments = {}

    list_assets = all_assets.copy()
    random.shuffle(list_assets)
    list_persons = sorted(persons, key=lambda person: person_score[person], reverse=True)
    list_assets = all_assets.copy()
    random.shuffle(list_assets)
    list_cfs = all_cfs.copy()

    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        if (chosen_cas, chosen_asset, chosen_cf) in required_timesteps:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # Calculate metrics
    total_trips_time = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Summarize the results
    for casualty, (asset, care_facility, ts) in assignments.items():
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
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0


    for index, mission in enumerate(missions_options):
        insults_dict = mission.insults_dict
        vitals_dict = mission.vitals_dict
        triage_score, triage_category, lsi_ts, rtd_ts, equipments_needed = return_triage_values(
            insults_dict=insults_dict, vitals_dict=vitals_dict)
        mission.triage_score = triage_score
        mission.triage_category = triage_category
        mission.lsi_ts = lsi_ts
        mission.rtd_ts = rtd_ts
        mission.equipments_needed = equipments_needed


    assignment_final = assignments.copy()
    columns = [
        'Isolated Casualty', 'Assigned MEDEVAC Asset', 'Assigned Care facility',
        'Route Distance (km)', 'Average Speed (km/hr)', 'Available Range',
        'Roundtrip Time (min)', 'Crew Hours Remaining',
        'Medical Triage Category', 'Medical Triage Score', 'Need Life Saving Intervention in: (min)',
        'Forecasted Survival Status', 'Return to Duty in: (days)',
        'Resource Requirement'
    ]
    df = pd.DataFrame(columns=columns)
    for person in persons:
        assigned_asset = None
        assigned_cf = None
        roundtrip_time_min = None
        roundtrip_distance_km = None
        average_speed_kmph = None
        available_range_km = None
        crew_hrs_remaining = None
        triage_category = None
        triage_score = None
        lsi = None
        rtd = None
        resource = None
        survival_status = None

        for mission in missions_options:
            if mission.patient_name == person:
                triage_category = mission.triage_category
                triage_score = mission.triage_score
                lsi = round(mission.lsi_ts * 60, 2)
                rtd = round(mission.rtd_ts / 24, 2)
                resource = mission.equipments_needed

        if person in assignment_final.keys():
            survival_status = 1
            assigned_asset = assignment_final[person][0]
            assigned_cf = assignment_final[person][1]
            roundtrip_time_min = round(assignment_final[person][2] * 60, 2)
            roundtrip_distance_km = round(req_distance[(person, assigned_asset, assigned_cf)], 2)

            for asset in assets:
                asset_record = asset.specifications_record
                if asset_record['asset_name'] == assigned_asset:
                    average_speed_kmph = asset_record['asset_speed_kmph']
                    available_range_km = asset_record['asset_range_in_km']
                    crew_hrs_remaining = asset_record['crew_duty_hrs']
        else:
            survival_status = 0

        row1 = pd.DataFrame([{
            'Isolated Casualty': person,
            'Assigned MEDEVAC Asset': assigned_asset,
            'Assigned Care facility': assigned_cf,
            'Route Distance (km)': roundtrip_distance_km,
            'Average Speed (km/hr)': average_speed_kmph,
            'Available Range': available_range_km,
            'Roundtrip Time (min)': roundtrip_time_min,
            'Crew Hours Remaining': crew_hrs_remaining,
            'Medical Triage Category': triage_category,
            'Medical Triage Score': triage_score,
            'Need Life Saving Intervention in: (min)': lsi,
            'Forecasted Survival Status': survival_status,
            'Return to Duty in: (days)': rtd,
            'Resource Requirement': resource
        }])
        df = pd.concat([df, row1], ignore_index=True)
    print(df)
    print(assignment_final)
    # # Define the CSV file path
    csv_file_path = f'sample_single_obj_triage.csv'

    # Append the DataFrame to the CSV file
    df.to_csv(csv_file_path, mode='w', header=True, index=True)

    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req

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

    required_timesteps, req_distance = get_required_timestamps_dict(persons=persons, all_assets=all_assets,
                                                                    all_cfs=all_cfs,
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

    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        if (chosen_cas, chosen_asset, chosen_cf) in required_timesteps:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # Calculate metrics
    total_trips_time = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Summarize the results
    for casualty, (asset, care_facility, ts) in assignments.items():
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
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0


    for index, mission in enumerate(missions_options):
        insults_dict = mission.insults_dict
        vitals_dict = mission.vitals_dict
        triage_score, triage_category, lsi_ts, rtd_ts, equipments_needed = return_triage_values(
            insults_dict=insults_dict, vitals_dict=vitals_dict)
        mission.triage_score = triage_score
        mission.triage_category = triage_category
        mission.lsi_ts = lsi_ts
        mission.rtd_ts = rtd_ts
        mission.equipments_needed = equipments_needed


    assignment_final = assignments.copy()
    columns = [
        'Isolated Casualty', 'Assigned MEDEVAC Asset', 'Assigned Care facility',
        'Route Distance (km)', 'Average Speed (km/hr)', 'Available Range',
        'Roundtrip Time (min)', 'Crew Hours Remaining',
        'Medical Triage Category', 'Medical Triage Score', 'Need Life Saving Intervention in: (min)',
        'Forecasted Survival Status', 'Return to Duty in: (days)',
        'Resource Requirement'
    ]
    df = pd.DataFrame(columns=columns)
    for person in persons:
        assigned_asset = None
        assigned_cf = None
        roundtrip_time_min = None
        roundtrip_distance_km = None
        average_speed_kmph = None
        available_range_km = None
        crew_hrs_remaining = None
        triage_category = None
        triage_score = None
        lsi = None
        rtd = None
        resource = None
        survival_status = None

        for mission in missions_options:
            if mission.patient_name == person:
                triage_category = mission.triage_category
                triage_score = mission.triage_score
                lsi = round(mission.lsi_ts * 60, 2)
                rtd = round(mission.rtd_ts / 24, 2)
                resource = mission.equipments_needed

        if person in assignment_final.keys():
            survival_status = 1
            assigned_asset = assignment_final[person][0]
            assigned_cf = assignment_final[person][1]
            roundtrip_time_min = round(assignment_final[person][2] * 60, 2)
            roundtrip_distance_km = round(req_distance[(person, assigned_asset, assigned_cf)], 2)

            for asset in assets:
                asset_record = asset.specifications_record
                if asset_record['asset_name'] == assigned_asset:
                    average_speed_kmph = asset_record['asset_speed_kmph']
                    available_range_km = asset_record['asset_range_in_km']
                    crew_hrs_remaining = asset_record['crew_duty_hrs']
        else:
            survival_status = 0

        row1 = pd.DataFrame([{
            'Isolated Casualty': person,
            'Assigned MEDEVAC Asset': assigned_asset,
            'Assigned Care facility': assigned_cf,
            'Route Distance (km)': roundtrip_distance_km,
            'Average Speed (km/hr)': average_speed_kmph,
            'Available Range': available_range_km,
            'Roundtrip Time (min)': roundtrip_time_min,
            'Crew Hours Remaining': crew_hrs_remaining,
            'Medical Triage Category': triage_category,
            'Medical Triage Score': triage_score,
            'Need Life Saving Intervention in: (min)': lsi,
            'Forecasted Survival Status': survival_status,
            'Return to Duty in: (days)': rtd,
            'Resource Requirement': resource
        }])
        df = pd.concat([df, row1], ignore_index=True)
    print(df)
    print(assignment_final)
    # # Define the CSV file path
    csv_file_path = f'sample_single_obj_rtd.csv'

    # Append the DataFrame to the CSV file
    df.to_csv(csv_file_path, mode='w', header=True, index=True)
    return len(served_casualties), total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req

def prioritized_equipments_assignment(missions_options, assets, care_facilities):
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

    required_timesteps, req_distance = get_required_timestamps_dict(persons=persons, all_assets=all_assets,
                                                                    all_cfs=all_cfs,
                                                                    all_lats_longs=all_lats_longs,
                                                                    curr_asset_location=curr_asset_location,
                                                                    assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                                    assets_speeds=assets_speeds,
                                                                    assets_time_ranges=assets_time_ranges)

    # Initialize dictionaries to store assignments and asset availability times
    assignments = {}

    list_persons = sorted(persons, key=lambda person: person_equipments_needed[person], reverse=True)
    list_assets = all_assets.copy()
    random.shuffle(list_assets)
    list_cfs = all_cfs.copy()

    for index, chosen_asset in enumerate(list_assets):

        chosen_cas = list_persons[index]
        chosen_cf = random.choice(list_cfs)
        if (chosen_cas, chosen_asset, chosen_cf) in required_timesteps:
            assignments[chosen_cas] = (chosen_asset, chosen_cf, required_timesteps[(chosen_cas, chosen_asset, chosen_cf)])

    # Calculate metrics
    total_trips_time = 0
    served_casualties = []
    triage_scores = []
    rtd_tss = []
    total_equipment_reqs = []

    # Summarize the results
    for casualty, (asset, care_facility, ts) in assignments.items():
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
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0


    for index, mission in enumerate(missions_options):
        insults_dict = mission.insults_dict
        vitals_dict = mission.vitals_dict
        triage_score, triage_category, lsi_ts, rtd_ts, equipments_needed = return_triage_values(
            insults_dict=insults_dict, vitals_dict=vitals_dict)
        mission.triage_score = triage_score
        mission.triage_category = triage_category
        mission.lsi_ts = lsi_ts
        mission.rtd_ts = rtd_ts
        mission.equipments_needed = equipments_needed


    assignment_final = assignments.copy()
    columns = [
        'Isolated Casualty', 'Assigned MEDEVAC Asset', 'Assigned Care facility',
        'Route Distance (km)', 'Average Speed (km/hr)', 'Available Range',
        'Roundtrip Time (min)', 'Crew Hours Remaining',
        'Medical Triage Category', 'Medical Triage Score', 'Need Life Saving Intervention in: (min)',
        'Forecasted Survival Status', 'Return to Duty in: (days)',
        'Resource Requirement'
    ]
    df = pd.DataFrame(columns=columns)
    for person in persons:
        assigned_asset = None
        assigned_cf = None
        roundtrip_time_min = None
        roundtrip_distance_km = None
        average_speed_kmph = None
        available_range_km = None
        crew_hrs_remaining = None
        triage_category = None
        triage_score = None
        lsi = None
        rtd = None
        resource = None
        survival_status = None

        for mission in missions_options:
            if mission.patient_name == person:
                triage_category = mission.triage_category
                triage_score = mission.triage_score
                lsi = round(mission.lsi_ts * 60, 2)
                rtd = round(mission.rtd_ts / 24, 2)
                resource = mission.equipments_needed

        if person in assignment_final.keys():
            survival_status = 1
            assigned_asset = assignment_final[person][0]
            assigned_cf = assignment_final[person][1]
            roundtrip_time_min = round(assignment_final[person][2] * 60, 2)
            roundtrip_distance_km = round(req_distance[(person, assigned_asset, assigned_cf)], 2)

            for asset in assets:
                asset_record = asset.specifications_record
                if asset_record['asset_name'] == assigned_asset:
                    average_speed_kmph = asset_record['asset_speed_kmph']
                    available_range_km = asset_record['asset_range_in_km']
                    crew_hrs_remaining = asset_record['crew_duty_hrs']
        else:
            survival_status = 0

        row1 = pd.DataFrame([{
            'Isolated Casualty': person,
            'Assigned MEDEVAC Asset': assigned_asset,
            'Assigned Care facility': assigned_cf,
            'Route Distance (km)': roundtrip_distance_km,
            'Average Speed (km/hr)': average_speed_kmph,
            'Available Range': available_range_km,
            'Roundtrip Time (min)': roundtrip_time_min,
            'Crew Hours Remaining': crew_hrs_remaining,
            'Medical Triage Category': triage_category,
            'Medical Triage Score': triage_score,
            'Need Life Saving Intervention in: (min)': lsi,
            'Forecasted Survival Status': survival_status,
            'Return to Duty in: (days)': rtd,
            'Resource Requirement': resource
        }])
        df = pd.concat([df, row1], ignore_index=True)
    print(df)
    print(assignment_final)
    # # Define the CSV file path
    csv_file_path = f'sample_single_obj_resources.csv'

    # Append the DataFrame to the CSV file
    df.to_csv(csv_file_path, mode='w', header=True, index=True)
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
    average_triage_score = sum(triage_scores) / len(triage_scores) if triage_scores else 0
    average_rtd_ts = sum(rtd_tss) / len(rtd_tss) if rtd_tss else None
    total_equipment_req = sum(total_equipment_reqs) if total_equipment_reqs else 0
    return num_casualties_served, total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req
def main(n_casualties, n_assets, n_cfs):

    # objectives = ['PRIMARY']
    objectives = ['REVERSE']
    # objectives = ['SITUATIONAL']

    # Generate random indices

    # cas_indexes = random.sample(range(1, 501), n_casualties)
    # assets_indexes = random.sample(range(1, 501), n_assets)
    # cfs_indexes = random.sample(range(1, 101), n_cfs)
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


    algo_mission_assets = FactoryAlgos.create_algo(mode=AlgoName.SINGLE_OBJ_SCHEDULER)
    mission_final_assets, solution_found, schedule_dict, all_persons, person_scores, person_lsi_ts, person_rtd_ts, person_equipments_needed, req_ts = algo_mission_assets.return_final_assignments_single_obj_scheduler(
        missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
        objectives=objectives)




    # num_cas_served, total_trips_time, average_triage_score, average_rtd_ts, total_equipment_req = get_required_values(triage_assignments=assignment_final, all_mission_options=all_mission_options)


    # GEt metrics for random baseline
    # num_served_cas_random, total_trips_time_random, average_triage_score_random, average_rtd_ts_random, total_equipment_req_random = random_baseline(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    # num_served_triage, total_trips_time_triage, average_triage_score_triage, average_rtd_ts_triage, total_equipment_req_triage = prioritized_triage_assignment(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    # num_served_rtd, total_trips_time_rtd, average_triage_score_rtd, average_rtd_ts_rtd, total_equipment_req_rtd = prioritized_rtd_assignment(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    # num_served_equipments, total_trips_time_equipments, average_triage_score_equipments, average_rtd_ts_equipments, total_equipment_req_equipments = prioritized_equipments_assignment(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities)
    #
    #
    # # Create a DataFrame with the required data
    # df = pd.DataFrame({
    #     'num_cas': [n_casualties],
    #     'num_assets': [n_assets],
    #     'solution_found_opt': [solution_found],
    #     'num_cas_served_opt': [num_cas_served],
    #     'total_trips_time_opt': [total_trips_time],
    #     'average_triage_score_opt': [average_triage_score],
    #     'average_rtd_time_opt': [average_rtd_ts],
    #     'total_equipment_req_opt': [total_equipment_req],
    #     'num_cas_served_random': [num_served_cas_random],
    #     'num_cas_served_triage': [num_served_triage],
    #     'num_cas_served_equipment': [num_served_equipments],
    #     'num_cas_served_rtd': [num_served_rtd],
    #     'total_trips_time_random': [total_trips_time_random],
    #     'total_trips_time_triage': [total_trips_time_triage],
    #     'total_trips_time_rtd': [total_trips_time_rtd],
    #     'total_trips_time_equipment': [total_trips_time_equipments],
    #     'average_triage_score_random': [average_triage_score_random],
    #     'average_triage_score_triage': [average_triage_score_triage],
    #     'average_triage_score_rtd': [average_triage_score_rtd],
    #     'average_triage_score_equipment': [average_triage_score_equipments],
    #     'average_rtd_time_random': [average_rtd_ts_random],
    #     'average_rtd_time_triage': [average_rtd_ts_triage],
    #     'average_rtd_time_rtd': [average_rtd_ts_rtd],
    #     'average_rtd_time_equipment': [average_rtd_ts_equipments],
    #     'total_equipment_req_random': [total_equipment_req_random],
    #     'total_equipment_req_triage': [total_equipment_req_triage],
    #     'total_equipment_req_rtd': [total_equipment_req_rtd],
    #     'total_equipment_req_equipment': [total_equipment_req_equipments]
    #
    #
    # })
    #
    #
    # # Define the CSV file path
    # csv_file_path = f'experiment_baseline_single_obj_{objectives[0]}.csv'
    #
    # # Append the DataFrame to the CSV file
    # if not os.path.isfile(csv_file_path):
    #     df.to_csv(csv_file_path, index=False)
    # else:
    #     df.to_csv(csv_file_path, mode='a', header=False, index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--n_casualties', type=int, default=10, help='number of casualties')
    parser.add_argument('--n_assets', type=int, default=5, help='number of assets')
    parser.add_argument('--n_cfs', type=int, default=1, help='number of care facilities')

    args = parser.parse_args()
    main(args.n_casualties, args.n_assets, args.n_cfs)