import random
import json
import os


# def generate_random_coordinates():
#     # Center point (you can adjust this to your specific area of interest)
#     center_latitude = 36.6661
#     center_longitude = -108.43415
#
#     # Calculate the min and max latitudes and longitudes based on the delta
#     delta_lat = 6.37  # corresponds to about 707.11 km
#     delta_lng = 7.94  # corresponds to about 707.11 km at this latitude
#
#     min_latitude = center_latitude - delta_lat / 2
#     max_latitude = center_latitude + delta_lat / 2
#     min_longitude = center_longitude - delta_lng / 2
#     max_longitude = center_longitude + delta_lng / 2
#
#     random_latitude = round(random.uniform(min_latitude, max_latitude), 5)
#     random_longitude = round(random.uniform(min_longitude, max_longitude), 5)
#
#     return random_latitude, random_longitude
def generate_random_coordinates():
    # Current Latitude and Longitude Ranges
    min_latitude = 31.3322
    max_latitude = 42.0000
    min_longitude = -114.8183
    max_longitude = -102.05

    # Calculate current differences
    lat_diff = max_latitude - min_latitude
    lng_diff = max_longitude - min_longitude

    # Scaling factor to achieve the target area
    scaling_factor = 1.322  # Based on the calculation above

    # Adjust differences
    new_lat_diff = lat_diff * scaling_factor
    new_lng_diff = lng_diff * scaling_factor

    # Calculate new latitude and longitude ranges
    center_latitude = (min_latitude + max_latitude) / 2
    center_longitude = (min_longitude + max_longitude) / 2

    new_min_latitude = center_latitude - new_lat_diff / 2
    new_max_latitude = center_latitude + new_lat_diff / 2
    new_min_longitude = center_longitude - new_lng_diff / 2
    new_max_longitude = center_longitude + new_lng_diff / 2

    # Generate random coordinates within the new ranges
    random_latitude = random.uniform(new_min_latitude, new_max_latitude)
    random_longitude = random.uniform(new_min_longitude, new_max_longitude)

    return random_latitude, random_longitude
# create casualty data
def create_casualty_data_sample(num_casualties):
    casualties_dict = {}
    # Generate NISS data
    for i in range(1, 101):
        cas_dict = {}
        cas_name = f'Casualty {i}'
        cas_latitude, cas_longitude = generate_random_coordinates()
        cas_dict['name'] = cas_name
        cas_dict['latitude'] = cas_latitude
        cas_dict['longitude'] = cas_longitude

        cas_dict['sbp'] = None
        cas_dict['rr'] = None
        cas_dict['gcs'] = None

        cas_dict['insult - External Hemorrhage - Head'] = random.randint(0, 6)
        cas_dict['insult - External Hemorrhage - Extremity'] = random.randint(0, 6)
        cas_dict['insult - External Hemorrhage - Trunk'] = random.randint(0, 6)
        cas_dict['insult - External Hemorrhage - Pelvis'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Head'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Extremity'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Trunk'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Pelvis'] = random.randint(0, 6)

        casualties_dict[i] = cas_dict
    # Generate RTS data
    for i in range(101, 201):
        cas_dict = {}
        cas_name = f'Casualty {i}'
        cas_latitude, cas_longitude = generate_random_coordinates()
        cas_dict['name'] = cas_name
        cas_dict['latitude'] = cas_latitude
        cas_dict['longitude'] = cas_longitude

        cas_dict['sbp'] = round(random.uniform(0,200),2)
        cas_dict['rr'] = round(random.uniform(0,200), 2)
        cas_dict['gcs'] = random.randint(3,15)

        cas_dict['insult - External Hemorrhage - Head'] = None
        cas_dict['insult - External Hemorrhage - Extremity'] = None
        cas_dict['insult - External Hemorrhage - Trunk'] = None
        cas_dict['insult - External Hemorrhage - Pelvis'] = None
        cas_dict['insult - Thermal Burn - Head'] = None
        cas_dict['insult - Thermal Burn - Extremity'] = None
        cas_dict['insult - Thermal Burn - Trunk'] = None
        cas_dict['insult - Thermal Burn - Pelvis'] = None

        casualties_dict[i] = cas_dict
    # Generate life data
    for i in range(201, 501):
        cas_dict = {}
        cas_name = f'Casualty {i}'
        cas_latitude, cas_longitude = generate_random_coordinates()
        cas_dict['name'] = cas_name
        cas_dict['latitude'] = cas_latitude
        cas_dict['longitude'] = cas_longitude

        cas_dict['sbp'] = round(random.uniform(0, 200),2)
        cas_dict['rr'] = round(random.uniform(0, 200), 2)
        cas_dict['gcs'] = round(random.randint(3, 15), 2)

        cas_dict['insult - External Hemorrhage - Head'] = random.randint(0, 6)
        cas_dict['insult - External Hemorrhage - Extremity'] = random.randint(0, 6)
        cas_dict['insult - External Hemorrhage - Trunk'] = random.randint(0, 6)
        cas_dict['insult - External Hemorrhage - Pelvis'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Head'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Extremity'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Trunk'] = random.randint(0, 6)
        cas_dict['insult - Thermal Burn - Pelvis'] = random.randint(0, 6)

        casualties_dict[i] = cas_dict
    return casualties_dict

# create asset data
def create_asset_data_sample(num_assets):
    assets_dict = {}
    for i in range(1, num_assets + 1):
        ass_dict = {}
        ass_name = f'Asset {i}'
        ass_latitude, ass_longitude = generate_random_coordinates()
        ass_range_km, ass_speed_kph = random.choice([(670,280)])
        crew_duty_hrs = random.uniform(1,10)
        ass_dict['name'] = ass_name
        ass_dict['latitude'] = ass_latitude
        ass_dict['longitude'] = ass_longitude
        ass_dict['range_km'] = ass_range_km
        ass_dict['speed_kph'] = ass_speed_kph
        ass_dict['crew_duty_hrs'] = crew_duty_hrs
        # ass_dict['vtol'] = random.randint(0,1)
        # if ass_dict['vtol'] == 1:
        #     ass_dict['ground'] = 0
        # else:
        #     ass_dict['ground'] = 1
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

