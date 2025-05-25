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

class MissionFinalAssetsTriage(FinalAssets):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def use_milp_primary_triage(self, persons, assets, hospitals, person_score, required_timesteps):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(
            Y[p] * person_score[p] - 0.1 * Z[r, p, h] * required_timesteps[(p, r, h)] for p in persons for r in assets
            for h in hospitals if (p,r,h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p,r,h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p,r,h) in required_timesteps) <= 1

        # Optimize the model
        m.optimize()

        # Extract the solution
        assignment = {}
        for r in assets:
            for p in persons:
                for h in hospitals:
                    if (p,r,h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                        assignment[p] = (r, h, required_timesteps[(p, r, h)])

        return assignment

    def use_milp_reverse_triage(self, persons, assets, hospitals, required_timesteps, available_timesteps):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(Y[p]*(1/(1+available_timesteps[p])) - 0.1*Z[r, p, h] * required_timesteps[(p, r, h)] for p in persons for r in assets for h in hospitals if (p, r, h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p,r,h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p,r,h) in required_timesteps) <= 1

        # Optimize the model
        m.optimize()

        # Extract the solution
        assignment = {}
        for r in assets:
            for p in persons:
                for h in hospitals:
                    if (p,r,h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                        assignment[p] = (r, h, required_timesteps[(p, r, h)])

        return assignment

    def use_milp_situational_triage(self, persons, assets, hospitals, person_score, required_timesteps, available_timesteps):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(Y[p]*(person_score[p]+(1/(1+available_timesteps[p]))) - 0.1*Z[r, p, h] * required_timesteps[(p, r, h)] for p in persons for r in assets for h in hospitals if (p, r, h) in required_timesteps))
        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p,r,h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p,r,h) in required_timesteps) <= 1

        # Optimize the model
        m.optimize()

        # Extract the solution
        assignment = {}
        for r in assets:
            for p in persons:
                for h in hospitals:
                    if (p,r,h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
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

    def return_mission_final_asset_triage(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities = list[CareFacility])-> list[MissionFinalAssets]:


        persons = []
        all_assets = []
        person_score = {}
        person_ts_available = {}
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

            possible_assets = mission.assets_possible
            possible_care_facilities = mission.care_facilities_possible
            person_score[patient_name] = 1-(patient_triage_score/100)
            person_ts_available[patient_name] = patient_ts_available
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
        assignment_primary = self.use_milp_primary_triage(persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score, required_timesteps=required_timesteps)
        assignment_reverse = self.use_milp_reverse_triage(persons=persons, assets=all_assets, hospitals=all_cfs, available_timesteps=person_ts_available, required_timesteps=required_timesteps)
        assignment_situational = self.use_milp_situational_triage(persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score, available_timesteps=person_ts_available, required_timesteps=required_timesteps)

        print(assignment_primary)
        print(assignment_reverse)
        print(assignment_situational)
        print(persons)
        print(missions_options)
        print(assets)
        print(care_facilities)
        print(all_assets)

        asset_tuples_primary = []
        asset_tuples_reverse = []
        asset_tuples_situational = []
        print('\n\n Primary triage assignment')
        for person, (asset, cf, ts) in assignment_primary.items():
            print(person, (asset, cf, ts))
            print(person, asset)
            asset_tuples_primary.append((asset,person))
        print('\n\n Reverse triage assignment')
        for person, (asset, cf, ts) in assignment_reverse.items():
            print(person, (asset, cf, ts))
            print(person, asset)
            asset_tuples_reverse.append((asset,person))
        print('\n\n Situational triage assignment')
        for person, (asset, cf, ts) in assignment_situational.items():
            print(person, (asset, cf, ts))
            print(person, asset)
            asset_tuples_situational.append((asset,person))

        pr.reset()
        pr.reset_rules()
        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True
        pr.settings.parallel_computing = False
        graph = self.create_pyreason_graph(missions_options=missions_options, assets=assets, care_facilities=care_facilities)
        graphml_path = 'pyreason_input_graph_mission_assets_triage_types.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_mission_assets_triage_types.txt'
        self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
        rules_path = os.path.join(current_script_directory, rules_path)



        pr.load_graphml(graphml_path)
        pr.add_rules_from_file(rules_path, infer_edges=False)

        # Reason at t=0
        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t0_mission_assets_triage_types'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        edge_facts = []
        node_facts = []
        for person, (asset, cf, ts) in assignment_primary.items():
            fact_triage_assign = pr.fact_edge.Fact(f'f_{person}', (asset, person),
                                                 pr.label.Label('assign_primary_triage'),
                                                 pr.interval.closed(1, 1),
                                                 self.next_time,
                                                 self.next_time)
            edge_facts.append(fact_triage_assign)




        for person, (asset, cf, ts) in assignment_reverse.items():
            fact_triage_assign = pr.fact_edge.Fact(f'f_{person}', (asset, person),
                                                   pr.label.Label('assign_reverse_triage'),
                                                   pr.interval.closed(1, 1),
                                                   self.next_time,
                                                   self.next_time)
            edge_facts.append(fact_triage_assign)

        for person, (asset, cf, ts) in assignment_situational.items():
            fact_triage_assign = pr.fact_edge.Fact(f'f_{person}', (asset, person),
                                                   pr.label.Label('assign_situational_triage'),
                                                   pr.interval.closed(1, 1),
                                                   self.next_time,
                                                   self.next_time)
            edge_facts.append(fact_triage_assign)
        for p in persons:
            for a in all_assets:
                if (a,p) not in asset_tuples_primary:
                    fact_triage_assign_0 = pr.fact_edge.Fact(f'f_{p}_{a}_0', (a, p),
                                                             pr.label.Label('assign_primary_triage'),
                                                             pr.interval.closed(0, 0),
                                                             self.next_time,
                                                             self.next_time)
                    edge_facts.append(fact_triage_assign_0)
        for p in persons:
            for a in all_assets:
                if (a,p) not in asset_tuples_reverse:
                    fact_triage_assign_0 = pr.fact_edge.Fact(f'f_{p}_{a}_0', (a, p),
                                                             pr.label.Label('assign_reverse_triage'),
                                                             pr.interval.closed(0, 0),
                                                             self.next_time,
                                                             self.next_time)
                    edge_facts.append(fact_triage_assign_0)
        for p in persons:
            for a in all_assets:
                if (a,p) not in asset_tuples_situational:
                    fact_triage_assign_0 = pr.fact_edge.Fact(f'f_{p}_{a}_0', (a, p),
                                                             pr.label.Label('assign_situational_triage'),
                                                             pr.interval.closed(0, 0),
                                                             self.next_time,
                                                             self.next_time)
                    edge_facts.append(fact_triage_assign_0)

        # Reason at t=1
        self.interpretation = pr.reason(again=True, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t1_mission_assets_triage_types'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)









        # return mission_final_assets


