from services.service_mission_final_assets.AlgoMissionFinalAssets import FinalAssets

from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

from datetime import datetime
import networkx as nx
import pyreason as pr
import os
import math

from mip import Model, xsum, maximize, BINARY, OptimizationStatus

class MissionFinalAssetsOptConstraints(FinalAssets):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def use_milp(self, persons, assets, hospitals, person_score, required_timesteps, available_timesteps, equipments_needed, weight_available_ts = 1, weight_need_equipment=1):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(
            Y[p] * (person_score[p] + weight_need_equipment * equipments_needed[p] + weight_available_ts*(1 / (1 + available_timesteps[p]))) - 0.1 * Z[r, p, h] * required_timesteps[
                (p, r, h)] for p in persons for r in assets for h in hospitals if (p, r, h) in required_timesteps))
        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1

        # Optimize the model
        m.optimize()

        # Extract the solution
        assignment = {}
        for r in assets:
            for p in persons:
                for h in hospitals:
                    if (p, r, h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                        assignment[p] = (r, h, required_timesteps[(p, r, h)])

        return assignment

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
        # time_minutes = time_hours * 60
        # time_minutes = int(math.ceil(time_minutes))

        return time_hours
    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'
    def create_pyreason_graph(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities: list[CareFacility]):
        g = nx.DiGraph()

        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            g.add_node(patient_name, type_casualty='1,1')
        for index, asset in enumerate(assets):
            record = asset.specifications_record
            asset_name = record['asset_name']
            g.add_node(asset_name, type_asset='1,1')
        for index, cf in enumerate(care_facilities):
            record = cf.specifications_record
            cf_name = record['cf_name']
            g.add_node(cf_name, type_cf='1,1')

        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            for index, asset in enumerate(assets):
                record = asset.specifications_record
                asset_name = record['asset_name']
                g.add_edge(asset_name, patient_name, assign_primary_triage='0,1', assign_reverse_triage='0,1', assign_situational_triage='0,1', assign_common_triage='0,1', assign_primary_reverse_triage='0,1',
                           assign_primary_situational_triage='0,1', assign_reverse_situational_triage='0,1', assign_primary_only_triage='0,1', assign_reverse_only_triage='0,1', assign_situational_only_triage='0,1')


        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_final_asset_OptConstraints(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities = list[CareFacility], weight_available_ts = 1, weight_need_equipment=1)-> list[MissionFinalAssets]:


        persons = []
        all_assets = []
        person_score = {}
        person_ts_available = {}
        person_need_equipments = {}
        all_cfs = []
        required_timesteps = {}
        curr_asset_location = {}
        all_lats_longs = {}
        assets_speeds = {}
        assets_time_ranges = {}
        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            patient_triage_score = mission.triage_score
            patient_location = mission.location
            patient_ts_available = mission.available_ts
            patient_need_equipment = mission.need_equipments

            possible_assets = mission.assets_possible
            possible_care_facilities = mission.care_facilities_possible
            person_score[patient_name] = 1-(patient_triage_score/100)
            person_ts_available[patient_name] = patient_ts_available
            person_need_equipments[patient_name] = patient_need_equipment
            persons.append(patient_name)
            all_lats_longs[patient_name] = patient_location
        for index, asset in enumerate(assets):
            record = asset.specifications_record
            asset_name = record['asset_name']
            asset_range_in_km = record['asset_range_in_km']
            asset_speed_kmph = record['asset_speed_kmph']
            asset_time_range = asset_range_in_km/asset_speed_kmph
            print(asset_name, asset_range_in_km, asset_speed_kmph, asset_time_range)
            asset_location = record['location']
            all_assets.append(asset_name)
            assets_time_ranges[asset_name] = asset_time_range
            curr_asset_location[asset_name] = asset_name
            assets_speeds[asset_name] = asset_speed_kmph
            all_lats_longs[asset_name] = asset_location
        for index, cf in enumerate(care_facilities):
            record = cf.specifications_record
            cf_name = record['cf_name']
            cf_location = record['location']
            all_cfs.append(cf_name)
            all_lats_longs[cf_name] = cf_location

        for person in persons:
            person_lat = all_lats_longs[person][0]
            person_long = all_lats_longs[person][1]
            for asset in all_assets:
                source_location = curr_asset_location[asset]
                asset_lat = all_lats_longs[source_location][0]
                asset_long = all_lats_longs[source_location][1]
                for cf in all_cfs:
                    cf_lat = all_lats_longs[cf][0]
                    cf_lon = all_lats_longs[cf][1]
                    # print(person, asset, source_location, cf)
                    trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat, person_long) + self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                    trip_time = trip_distance/assets_speeds[asset]

                    if trip_time <= assets_time_ranges[asset]:
                        required_timesteps[(person, asset, cf)] = math.ceil(trip_time)

        # Get schedul;e iteration 1
        assignment_primary = self.use_milp(persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score, required_timesteps=required_timesteps, available_timesteps=person_ts_available, equipments_needed=person_need_equipments,
                                           weight_available_ts = weight_available_ts, weight_need_equipment=weight_need_equipment)
        print('\n\n Primary triage assignment')
        for person, (asset, cf, ts) in assignment_primary.items():
            print(person, (asset, cf, ts))




        # return mission_final_assets


