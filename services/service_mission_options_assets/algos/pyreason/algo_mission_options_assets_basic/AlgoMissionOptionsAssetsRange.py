from services.service_mission_options_assets.AlgoMissionOptionsAssets import OptionsAssets

from services.models.ModelMissionOptionsResourcesCombinations import MissionOptionsResourcesCombinations
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

from datetime import datetime
import networkx as nx
import pyreason as pr
import os
import math

class MissionOptionsAssetsRange(OptionsAssets):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def haversine_distance(self, lat1, lon1, lat2, lon2):
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

    def travel_time(self, lat1, lon1, lat2, lon2, speed):
        # Calculate the distance using the Haversine formula
        distance = self.haversine_distance(lat1, lon1, lat2, lon2)

        # Calculate the time in hours
        time_hours = distance / speed

        # Convert time to minutes
        time_minutes = time_hours * 60
        time_minutes = int(math.ceil(time_minutes))

        return time_minutes

    def append_to_rules(self, file_path, line):
        with open(file_path, 'a') as file:
            file.write('\n' + line + '\n')

    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'
    def create_pyreason_graph(self, mission_requirements: list[MissionRequirements], assets: list[Asset], care_facilities: list[CareFacility]):
        g = nx.DiGraph()
        # Model mission requirements
        for index,mission in enumerate(mission_requirements):
            record = mission.mission_requirements_record
            if record['weather_condition'] == 'clear':
                weather_condition_clear = '1,1'
            elif record['weather_condition'] == 'unclear':
                weather_condition_clear = '0,0'
            g.add_node(record['name'],
                       type_mission = '1,1',
                       mission_id = index+2,
                       medevac_needed = self.get_pyreason_bool(record['medevac_needed']),
                       evac_needed = self.get_pyreason_bool(record['evac_needed']),
                       resupply_needed = self.get_pyreason_bool(record['resupply_needed']),
                       require_vtol=self.get_pyreason_bool(record['require_vtol']),
                       require_ctol = self.get_pyreason_bool(record['require_ctol']),
                       require_ground = self.get_pyreason_bool(record['require_ground_vehicle']),
                       litters_spaces_required = int(record['litters_spaces_required']),
                       ambulatory_spaces_required = int(record['ambulatory_spaces_required']),
                       weather_condition_clear = weather_condition_clear,
                       day_mission = self.get_pyreason_bool(record['day_mission']),
                       night_mission = self.get_pyreason_bool(record['night_mission']),
                       require_iv_provisions = self.get_pyreason_bool(record['require_iv_provisions']),
                       require_medical_monitoring_system = self.get_pyreason_bool(record['require_medical_monitoring_system']),
                       require_life_support_equipment = self.get_pyreason_bool(record['require_life_support_equipment']),
                       require_oxygen_generation_system = self.get_pyreason_bool(record['require_oxygen_generation_system']),
                       require_patient_litter_lift_system = self.get_pyreason_bool(record['require_patient_litter_lift_system']))

        for index,mission in enumerate(mission_requirements):
            record = mission.mission_requirements_record
            cas_latitude = str(record['location'][0])
            cas_longitude = str(record['location'][1])
            name = record['name']
            g.add_edge(name, cas_latitude, casualty_latitude='1,1')
            g.add_edge(name, cas_longitude, casualty_longitude='1,1')

        for index,asset in enumerate(assets):
            record = asset.specifications_record
            if record['asset_type'] == 'vtol':
                asset_type_vtol = '1,1'
                asset_type_ctol = '0,0'
                asset_type_ground = '0,0'
            elif record['asset_type'] == 'ctol':
                asset_type_ctol = '1,1'
                asset_type_vtol = '0,0'
                asset_type_ground = '0,0'
            elif record['asset_type'] == 'ground':
                asset_type_ground = '1,1'
                asset_type_vtol = '0,0'
                asset_type_ctol = '0,0'
            if record['asset_status'] == 'available':
                asset_status_available = '1,1'
            elif record['asset_status'] == 'unavailable':
                asset_status_available = '0,0'
            if record['asset_mission_type'] == 'medevac':
                asset_mission_type_medevac = '1,1'
                asset_mission_type_evac = '0,0'
                asset_mission_type_resupply = '0,0'
            elif record['asset_mission_type'] == 'evac':
                asset_mission_type_evac = '1,1'
                asset_mission_type_medevac = '0,0'
                asset_mission_type_resupply = '0,0'
            elif record['asset_mission_type'] == 'resupply':
                asset_mission_type_resupply = '1,1'
                asset_mission_type_medevac = '0,0'
                asset_mission_type_evac = '0,0'
            g.add_node(record['asset_name'],
                       type_asset = '1,1',
                       asset_id = index+2,
                       asset_type_vtol=asset_type_vtol, asset_type_ctol=asset_type_ctol, asset_type_ground=asset_type_ground,
                       asset_status_available = asset_status_available,
                       asset_mission_type_medevac = asset_mission_type_medevac, asset_mission_type_evac =asset_mission_type_evac, asset_mission_type_resupply = asset_mission_type_resupply,
                       asset_litter_capacity = int(record['litter_capacity']), asset_ambulatory_capacity = int(record['ambulatory_capacity']),
                       operational_day=self.get_pyreason_bool(record['operational_day']),
                       operational_night=self.get_pyreason_bool(record['operational_night']),
                       operational_adverse_weather=self.get_pyreason_bool(record['operational_adverse_weather']),
                       has_iv_provisions=self.get_pyreason_bool(record['has_iv_provisions']),
                       has_medical_monitoring_system=self.get_pyreason_bool(record['has_medical_monitoring_system']),
                       has_life_support_equipment=self.get_pyreason_bool(record['has_life_support_equipment']),
                       has_oxygen_generation_system=self.get_pyreason_bool(record['has_oxygen_generation_system']),
                       has_patient_litter_lift_system=self.get_pyreason_bool(record['has_patient_litter_lift_system']),
                       )
        for mission in mission_requirements:
            record_mission = mission.mission_requirements_record
            mission_node = record_mission['name']
            for asset in assets:
                record_asset = asset.specifications_record
                asset_node = record_asset['asset_name']
                g.add_edge(mission_node, asset_node, option_assets = '0,0', mission_type_satisfied='0,0', mission_vehicle_satisfied='0,0', litter_ambulatory_satisfied='0,0', weather_satisfied='0,0',
                           day_night_satisfied='0,0', iv_provision_satisfied='0,0', medical_monitoring_system_satisfied='0,0', life_support_equipment_satisfied='0,0', oxygen_generation_system_satisfied='0,0',
                           patient_litter_lift_system_satisfied='0,0')
        for index,asset in enumerate(assets):
            record = asset.specifications_record
            asset_name = record['asset_name']
            asset_latitude = str(record['location'][0])
            asset_longitude = str(record['location'][1])
            asset_range_in_kms = record['asset_range_in_km']
            asset_speed_in_kmph = record['asset_speed_kmph']
            g.add_edge(asset_name, asset_latitude, asset_latitude='1,1')
            g.add_edge(asset_name, asset_longitude, asset_longitude='1,1')
            g.add_edge(asset_name, asset_range_in_kms, range_in_km = '1,1')
            g.add_edge(asset_name, asset_speed_in_kmph, asset_speed_km_per_hour = '1,1')

        for index,cf in enumerate(care_facilities):
            record = cf.specifications_record
            cf_name = record['cf_name']
            cf_latitude = str(record['location'][0])
            cf_longitude = str(record['location'][1])
            g.add_node(cf_name, type_care_facility='1,1')
            g.add_edge(cf_name, cf_latitude, cf_latitude='1,1')
            g.add_edge(cf_name, cf_longitude, cf_longitude='1,1')
        for mission in mission_requirements:
            record_mission = mission.mission_requirements_record
            cas_name = record_mission['name']
            possible_cfs = record_mission['care_facilities_possible']
            for cf in possible_cfs:
                g.add_edge(cas_name, cf, cf_possible='1,1')

        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_options_assets_range(self, mission_requirements: list[MissionRequirements], assets: list[Asset], care_facilities: list[CareFacility])-> list[MissionOptionsResourcesCombinations]:


        mission_options_resources = []
        # Set pyreason settings
        graph = self.create_pyreason_graph(mission_requirements, assets, care_facilities=care_facilities)
        graphml_path = 'pyreason_input_graph_mission_requirements_assets_range.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_mission_requirements_to_mission_options_resources.txt'
        self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
        rules_path = os.path.join(current_script_directory, rules_path)

        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True

        pr.load_graphml(graphml_path)
        pr.add_rules_from_file(rules_path, infer_edges=False)

        # Reason at t=0
        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t0_mission_requirements_to_mission_options_assets'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)
        dict_mission_assets = {}
        field = 'option_assets'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        p_name = df['component'][i][0]
                        a_name = df['component'][i][1]
                        if p_name not in dict_mission_assets:
                            dict_mission_assets[p_name] = [a_name]
                        else:
                            dict_mission_assets[p_name].append(a_name)
        # print(dict_mission_assets)

        ## Later repace with pyreason block

        dict_cas_location = {}
        dict_cas_cfs = {}
        dict_cas_resources ={}

        dict_asset_location = {}
        dict_asset_range = {}
        dict_asset_speed = {}

        dict_cf_location = {}

        for mission in mission_requirements:
            record = mission.mission_requirements_record
            name = record['name']
            latitude = record['location'][0]
            longitude = record['location'][1]
            possible_cfs = record['care_facilities_possible']

            dict_cas_location[name] = [latitude, longitude]
            dict_cas_cfs[name] = possible_cfs

        for asset in assets:
            record = asset.specifications_record
            asset_name = record['asset_name']
            latitude = record['location'][0]
            longitude = record['location'][1]
            asset_range = record['asset_range_in_km']
            asset_speed_kmph = record['asset_speed_kmph']

            dict_asset_location[asset_name] = [latitude, longitude]
            dict_asset_speed[asset_name] = asset_speed_kmph
            dict_asset_range[asset_name] = asset_range
        for cf in care_facilities:
            record = cf.specifications_record
            cf_name = record['cf_name']
            latitude = record['location'][0]
            longitude = record['location'][1]

            dict_cf_location[cf_name] = [latitude, longitude]

        for cas_name, possible_assets in dict_mission_assets.items():

            for asset in possible_assets:
                range_asset = dict_asset_range[asset]
                for cf in dict_cas_cfs[cas_name]:
                    distance_asset_cas = self.haversine_distance(dict_asset_location[asset][0], dict_asset_location[asset][1],
                                                                 dict_cas_location[cas_name][0], dict_cas_location[cas_name][1])
                    distance_cas_cf = self.haversine_distance(dict_cas_location[cas_name][0], dict_cas_location[cas_name][1],
                                                              dict_cf_location[cf][0], dict_cf_location[cf][1])
                    total_distance = distance_asset_cas + distance_cas_cf

                    if range_asset > total_distance:
                        if cas_name not in dict_cas_resources:
                            dict_cas_resources[cas_name] = [(asset, cf)]
                        else:
                            dict_cas_resources[cas_name].append((asset, cf))
        # print(dict_cas_resources)

        for key, value in dict_cas_resources.items():
            mission_options_resources.append(
                MissionOptionsResourcesCombinations(
                    patient_name = key,
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name='pyreason_basic',
                    resources_possible=value,
                    assets_details=None,
                    confidence=1.0,
                    rationale=None,
                    interaction=None
                )
            )




        return mission_options_resources


