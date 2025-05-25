import random
import json
import os
def generate_random_coordinates():
    # Latitude range for
    min_latitude = 31.3322
    max_latitude = 42.0000

    # Longitude range for
    min_longitude = -114.8183
    max_longitude = -102.05

    random_latitude = random.uniform(min_latitude, max_latitude)
    random_longitude = random.uniform(min_longitude, max_longitude)

    return random_latitude, random_longitude

# create casualty data
def create_casualty_data_sample(num_casualties):
    casualties_dict = {}
    for i in range(1, num_casualties+1):
        cas_dict = {}
        cas_name = f'Casualty {i}'
        cas_triage_score = random.uniform(1,100)
        cas_latitude, cas_longitude = generate_random_coordinates()
        cas_dict['name'] = cas_name
        cas_dict['triage_score'] = cas_triage_score
        cas_dict['latitude'] = cas_latitude
        cas_dict['longitude'] = cas_longitude
        if 0 <= cas_triage_score <= 21:
            cas_dict['rtd_ts'] = random.uniform(80, 100)
        elif 21 <= cas_triage_score <= 41:
            cas_dict['rtd_ts'] = random.uniform(60, 80)
        elif 41 <= cas_triage_score <= 61:
            cas_dict['rtd_ts'] = random.uniform(40, 60)
        elif 61 <= cas_triage_score <= 81:
            cas_dict['rtd_ts'] = random.uniform(20, 40)
        elif 81 <= cas_triage_score <= 101:
            cas_dict['rtd_ts'] = random.uniform(1, 20)
        else:
            print(cas_triage_score)
            # Handle cases where the score is outside the expected range
            raise ValueError("cas_triage_score is out of expected range (0-100).")

        cas_dict['equipments_needed'] = random.randint(0,10)
        casualties_dict[i] = cas_dict
    return casualties_dict

# create asset data
def create_asset_data_sample(num_assets):
    assets_dict = {}
    for i in range(1, num_assets + 1):
        ass_dict = {}
        ass_name = f'Asset {i}'
        ass_latitude, ass_longitude = generate_random_coordinates()
        ass_range_km, ass_speed_kph = random.choice([(741,315), (603,126), (1111,357), (5250, 670)])
        crew_duty_hrs = random.randint(0,8)
        ass_dict['name'] = ass_name
        ass_dict['latitude'] = ass_latitude
        ass_dict['longitude'] = ass_longitude
        ass_dict['range_km'] = ass_range_km
        ass_dict['speed_kph'] = ass_speed_kph
        ass_dict['crew_duty_hrs'] = crew_duty_hrs
        ass_dict['vtol'] = random.randint(0,1)
        if ass_dict['vtol'] == 1:
            ass_dict['ground'] = 0
        else:
            ass_dict['ground'] = 1
        assets_dict[i] = ass_dict
    return assets_dict

def create_cf_data_sample(num_cfs):
    cfs_dict = {}
    for i in range(1, num_cfs+1):
        cf_dict = {}
        cf_name = f'Care Facility {i}'
        cf_latitude, cf_longitude = generate_random_coordinates()

        cf_dict['name'] = cf_name
        cf_dict['latitude'] = cf_latitude
        cf_dict['longitude'] = cf_longitude
        cfs_dict[i] = cf_dict
    return cfs_dict



casualties = create_casualty_data_sample(500)
assets = create_asset_data_sample(500)
care_facilities = create_cf_data_sample(100)
folder_name = 'casualty_dataset'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
# Writing to a JSON file
for i in range(1,501):
    with open(f'casualty_dataset/{i}.json', 'w') as json_file:
        json.dump(casualties[i], json_file)
folder_name = 'asset_dataset'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
# Writing to a JSON file
for i in range(1,501):
    with open(f'asset_dataset/{i}.json', 'w') as json_file:
        json.dump(assets[i], json_file)
folder_name = 'cf_dataset'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
# Writing to a JSON file
for i in range(1,101):
    with open(f'cf_dataset/{i}.json', 'w') as json_file:
        json.dump(care_facilities[i], json_file)

