import pandas as pd

from services.service_optimization.ServiceOptimizationMethods import OptimizationMethods
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility

from datetime import datetime
import networkx as nx
import pyreason as pr
import os
import math
import time
import tracemalloc
from mip import Model, xsum, maximize, BINARY, OptimizationStatus
import numpy as np
# import matplotlib.pyplot as plt


class OptimizationSingleObjScheduler(OptimizationMethods):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def use_milp_primary_triage(self, persons, assets, hospitals, person_score, required_timesteps, required_timesteps_lsi_only, person_lsi_ts, constraint_lsi = True):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        # m.objective = maximize(xsum(
        #     Y[p] * person_score[p] - 0.1 * Z[r, p, h] * required_timesteps[(p, r, h)] for p in persons for r in assets
        #     for h in hospitals if (p, r, h) in required_timesteps))
        # m.objective = maximize(xsum(
        #     Y[p] +10* Y[p] * person_score[p] for p in persons) + xsum(
        #     (1 / (1 + required_timesteps[(p, r, h)])) * Z[r, p, h] for p in persons for r in assets
        #     for h in hospitals if (p, r, h) in required_timesteps))
        m.objective = maximize(xsum(
            Y[p] + 10 * Y[p] * person_score[p] for p in persons) - 0.1*xsum(
            required_timesteps[(p, r, h)] * Z[r, p, h] for p in persons for r in assets
            for h in hospitals if (p, r, h) in required_timesteps))
        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1

        # New constraint: A casualty can only be assigned an asset and hospital if the required_timestep <= lsi_ts[p]
        if constraint_lsi:
            for p in persons:
                for r in assets:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps_lsi_only:
                            m += Z[r, p, h] * required_timesteps_lsi_only[(p, r, h)] <= person_lsi_ts[p]

        status = m.optimize()
        # Check if a solution was found
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print("Solution found:")
            # for p in persons:
            #     print(f"Y[{p}] = {Y[p].x}")
            #     for r in assets:
            #         for h in hospitals:
            #             if (p, r, h) in required_timesteps and Z[r, p, h].x > 0.99:  # Check if X[p, a, r] is set to 1
            #                 # print(f"X[{r}, {p}, {h}] = 1 (assigned)")
        elif status == OptimizationStatus.INFEASIBLE:
            print("No feasible solution found.")
        elif status == OptimizationStatus.UNBOUNDED:
            print("The problem is unbounded.")
        else:
            print("Optimization status:", status)

        # Extract the solution
        assignment = {}
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            for r in assets:
                for p in persons:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                            assignment[p] = (r, h, required_timesteps[(p, r, h)])

        return assignment

    def use_milp_reverse_triage(self, persons, assets, hospitals, required_timesteps, required_timesteps_lsi_only, rtd_timesteps, person_lsi_ts, constraint_lsi = True):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(
            Y[p] + 100*Y[p] * (1 / (1 + rtd_timesteps[p])) for p in persons) - 0.1*xsum(
            required_timesteps[(p, r, h)] * Z[r, p, h] for p in persons for r in assets
            for h in hospitals if (p, r, h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1

        # New constraint: A casualty can only be assigned an asset and hospital if the required_timestep <= lsi_ts[p]
        if constraint_lsi:
            for p in persons:
                for r in assets:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps_lsi_only:
                            m += Z[r, p, h] * required_timesteps_lsi_only[(p, r, h)] <= person_lsi_ts[p]
        # Optimize the model
        status = m.optimize()
        # Check if a solution was found
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print("Solution found:")
            # for p in persons:
            #     print(f"Y[{p}] = {Y[p].x}")
            #     for r in assets:
            #         for h in hospitals:
            #             if (p, r, h) in required_timesteps and Z[r, p, h].x > 0.99:  # Check if X[p, a, r] is set to 1
            #                 print(f"X[{r}, {p}, {h}] = 1 (assigned)")
        elif status == OptimizationStatus.INFEASIBLE:
            print("No feasible solution found.")
        elif status == OptimizationStatus.UNBOUNDED:
            print("The problem is unbounded.")
        else:
            print("Optimization status:", status)

        # Extract the solution
        assignment = {}
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            for r in assets:
                for p in persons:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                            assignment[p] = (r, h, required_timesteps[(p, r, h)])


        return assignment

    def use_milp_situational_triage(self, persons, assets, hospitals, required_timesteps, required_timesteps_lsi_only,
                                    person_equipments_needed, person_lsi_ts, constraint_lsi = True):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(
            Y[p] + Y[p] * person_equipments_needed[p] for p in persons) + xsum(
            (1 / (1 + required_timesteps[(p, r, h)])) * Z[r, p, h] for p in persons for r in assets
            for h in hospitals if (p, r, h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1
        # New constraint: A casualty can only be assigned an asset and hospital if the required_timestep <= lsi_ts[p]
        if constraint_lsi:
            for p in persons:
                for r in assets:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps_lsi_only:
                            m += Z[r, p, h] * required_timesteps_lsi_only[(p, r, h)] <= person_lsi_ts[p]
        # Optimize the model
        status = m.optimize()
        # Check if a solution was found
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print("Solution found:")
            # for p in persons:
            #     print(f"Y[{p}] = {Y[p].x}")
            #     for r in assets:
            #         for h in hospitals:
            #             if (p, r, h) in required_timesteps and Z[r, p, h].x > 0.99:  # Check if X[p, a, r] is set to 1
            #                 print(f"X[{r}, {p}, {h}] = 1 (assigned)")
        elif status == OptimizationStatus.INFEASIBLE:
            print("No feasible solution found.")
        elif status == OptimizationStatus.UNBOUNDED:
            print("The problem is unbounded.")
        else:
            print("Optimization status:", status)

        # Extract the solution
        assignment = {}
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            for r in assets:
                for p in persons:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                            assignment[p] = (r, h, required_timesteps[(p, r, h)])


        return assignment

    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'

    def create_pyreason_graph(self, missions_options: list[MissionOptionsAssets], assets: list[Asset],
                              care_facilities: list[CareFacility], objectives: list):

        g = nx.DiGraph()
        primary_triage = True if 'PRIMARY' in objectives else False
        reverse_triage = True if 'REVERSE' in objectives else False
        situational_triage = True if 'SITUATIONAL' in objectives else False

        if primary_triage:
            g.add_node('PRIMARY', use_opt='1,1', type_primary='1,1')
        else:
            g.add_node('PRIMARY', use_opt='0,0', type_primary='1,1')

        if reverse_triage:
            g.add_node('REVERSE', use_opt='1,1', type_reverse='1,1')
        else:
            g.add_node('REVERSE', use_opt='0,0', type_reverse='1,1')
        if situational_triage:
            g.add_node('SITUATIONAL', use_opt='1,1', type_situational='1,1')
        else:
            g.add_node('SITUATIONAL', use_opt='0,0', type_situational='1,1')
        g.add_node('None', type_none='1,1')

        g.add_node('final_solution', solution_found='0,1', type_final_solution='1,1', select_primary_solution='0,1',
                   select_reverse_triage='0,1', select_situational_triage='0,1')

        solution_possibilities = ['PRIMARY', 'REVERSE', 'SITUATIONAL', 'None']
        for sol in solution_possibilities:
            g.add_edge('final_solution', sol, accept_possible='0,1', accept_final='0,1')

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
            for index1, asset in enumerate(assets):
                record = asset.specifications_record
                asset_name = record['asset_name']
                g.add_edge(asset_name, patient_name, assign_asset_primary_triage='0,1',
                           assign_asset_reverse_triage='0,1', assign_asset_situational_triage='0,1',
                           assign_final_asset='0,1')
            for index2, cf in enumerate(care_facilities):
                record = cf.specifications_record
                cf_name = record['cf_name']
                g.add_edge(cf_name, patient_name, assign_cf_primary_triage='0,1', assign_cf_reverse_triage='0,1',
                           assign_cf_situational_triage='0,1', assign_final_cf='0,1')

        return g

    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

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

    def get_casualties_dicts(self, missions_options, persons, person_score, person_lsi_ts, person_rtd_ts,
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

    def get_assets_dicts(self, assets, assets_time_ranges, curr_asset_location,
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

    def get_cf_dicts(self, care_facilities, all_lats_longs):
        all_cfs = []
        for index, cf in enumerate(care_facilities):
            record = cf.specifications_record
            cf_name = record['cf_name']
            cf_location = record['location']
            all_cfs.append(cf_name)
            all_lats_longs[cf_name] = cf_location
        return all_cfs, all_lats_longs

    def get_required_timestamps_dict(self, persons, all_assets, all_cfs, all_lats_longs, curr_asset_location,
                                     assets_crew_duty_hrs, assets_speeds, assets_time_ranges):
        required_timesteps = {}
        required_distance = {}
        required_timesteps_lsi_only = {}
        required_timesteps_isop_cf = {}


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
                    asset_p_dist = self.haversine_distance(asset_lat, asset_long, person_lat, person_long)
                    asset_p_time = asset_p_dist/assets_speeds[asset]
                    trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat, person_long) + self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                    trip_time = trip_distance / assets_speeds[asset]
                    required_timesteps[(person, asset, cf)] = trip_time
                    required_distance[(person, asset, cf)] = trip_distance
                    required_timesteps_lsi_only[(person, asset, cf)] = asset_p_time


                    person_cf_d = self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                    person_cf_t = person_cf_d / assets_speeds[asset]

                    required_timesteps_isop_cf[(person, cf)] = person_cf_t


                    # if trip_time <= assets_time_ranges[asset] and trip_time < crew_duty_hrs:
                    #     required_timesteps[(person, asset, cf)] = trip_time
                    #     required_distance[(person, asset, cf)] = trip_distance
        return required_timesteps, required_distance, required_timesteps_lsi_only, required_timesteps_isop_cf

    def run_opt_problems(self, persons: list, all_assets: list, all_cfs, person_score: dict, person_lsi_ts: dict, required_timesteps: dict, required_timesteps_lsi_only: dict,
                         person_rtd_ts: dict, person_equipments_needed: dict,
                         run_primary: bool, run_reverse: bool, run_situational: bool):


        assignment = None
        if run_primary:
            assignment = self.use_milp_primary_triage(
                persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score,
                required_timesteps=required_timesteps, required_timesteps_lsi_only= required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts)
        if run_reverse:
            assignment = self.use_milp_reverse_triage(
                persons=persons, assets=all_assets, hospitals=all_cfs, rtd_timesteps=person_rtd_ts,
                required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts)
        if run_situational:
            assignment = self.use_milp_situational_triage(
                persons=persons, assets=all_assets, hospitals=all_cfs,
                person_equipments_needed=person_equipments_needed, required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts)

        return assignment


    def initialize_pyreason(self, missions_options, assets, care_facilities, objectives):
        pr.reset()
        pr.reset_rules()
        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True

        graph = self.create_pyreason_graph(missions_options=missions_options, assets=assets,
                                           care_facilities=care_facilities, objectives=objectives)
        graphml_path = 'pyreason_single_obj.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_triage_types.txt'
        self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
        rules_path = os.path.join(current_script_directory, rules_path)
        pr.load_graphml(graphml_path)
        pr.add_rules_from_file(rules_path, infer_edges=False)
        # Reason at t=0
        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t0_triage_singleObj'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

    def frame_opt_problems(self, missions_options, assets, care_facilities):

        dict_optimization_instances = {}

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
        assets_speeds = {}
        assets_time_ranges = {}
        assets_crew_duty_hrs = {}

        persons, person_score, person_lsi_ts, person_rtd_ts, person_equipments_needed, all_lats_longs = self.get_casualties_dicts(
            missions_options=missions_options, persons=persons, person_score=person_score,
            person_lsi_ts=person_lsi_ts, person_rtd_ts=person_rtd_ts,
            person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
        all_assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs = self.get_assets_dicts(
            assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location, assets_speeds=assets_speeds,
            all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)

        all_cfs, all_lats_longs = self.get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

        required_timesteps, required_distance, required_timesteps_lsi_only, required_timesteps_isop_cf = self.get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                               all_lats_longs=all_lats_longs,
                                                               curr_asset_location=curr_asset_location,
                                                               assets_crew_duty_hrs=assets_crew_duty_hrs,
                                                               assets_speeds=assets_speeds,
                                                               assets_time_ranges=assets_time_ranges)

        edge_facts = []
        node_facts = []


        # Reason at t=1
        self.interpretation = pr.reason(again=True, node_facts=node_facts, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t1_triage_singleObj'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        run_primary_triage = False
        run_reverse_triage = False
        run_situational_triage = False
        field = 'run_opt'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        triage_type = df['component'][i]
                        if triage_type == 'PRIMARY':
                            run_primary_triage = True
                        if triage_type == 'REVERSE':
                            run_reverse_triage = True
                        if triage_type == 'SITUATIONAL':
                            run_situational_triage = True

        dict_optimization_instances['persons'] = persons
        dict_optimization_instances['all_assets'] = all_assets
        dict_optimization_instances['all_cfs'] = all_cfs
        dict_optimization_instances['person_score'] = person_score
        dict_optimization_instances['required_timesteps'] = required_timesteps
        dict_optimization_instances['required_timesteps_lsi_only'] = required_timesteps_lsi_only
        dict_optimization_instances['required_timesteps_isop_cf'] = required_timesteps_isop_cf
        dict_optimization_instances['required_distance'] = required_distance
        dict_optimization_instances['person_rtd_ts'] = person_rtd_ts
        dict_optimization_instances['person_lsi_ts'] = person_lsi_ts
        dict_optimization_instances['person_equipments_needed'] = person_equipments_needed
        dict_optimization_instances['curr_asset_location'] = curr_asset_location
        dict_optimization_instances['assets_time_ranges'] = assets_time_ranges
        dict_optimization_instances['all_lats_longs'] = all_lats_longs
        dict_optimization_instances['assets_speeds'] = assets_speeds
        dict_optimization_instances['assets_crew_duty_hrs'] = assets_crew_duty_hrs

        dict_optimization_instances['run_primary_triage'] = run_primary_triage
        dict_optimization_instances['run_reverse_triage'] = run_reverse_triage
        dict_optimization_instances['run_situational_triage'] = run_situational_triage
        return dict_optimization_instances

    def run_optimization_instances(self, dict_optimization_instances):
        dict_optimization_results = {}
        persons = dict_optimization_instances['persons']
        all_assets = dict_optimization_instances['all_assets']
        all_cfs = dict_optimization_instances['all_cfs']
        person_score = dict_optimization_instances['person_score']
        required_timesteps = dict_optimization_instances['required_timesteps']
        required_timesteps_lsi_only = dict_optimization_instances['required_timesteps_lsi_only']
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_lsi_ts = dict_optimization_instances['person_lsi_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']
        run_primary_triage = dict_optimization_instances['run_primary_triage']
        run_reverse_triage = dict_optimization_instances['run_reverse_triage']
        run_situational_triage = dict_optimization_instances['run_situational_triage']


        assignment = self.run_opt_problems(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                                   person_score=person_score, required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only,
                                                   person_rtd_ts=person_rtd_ts,
                                                   person_lsi_ts=person_lsi_ts,
                                                   person_equipments_needed=person_equipments_needed, run_primary=run_primary_triage,
                                                   run_reverse=run_reverse_triage,
                                                   run_situational=run_situational_triage
                                                   )
        dict_optimization_results['assignment'] = assignment

        if pd.isna(assignment):
            dict_optimization_results['solution_found'] = False

            return dict_optimization_results
        else:


            dict_optimization_results['solution_found'] = True

            return dict_optimization_results
    def get_normalized_gcs(self, gcs):
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
    def get_normalized_sbp(self, sbp):
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

    def get_normalized_rr(self, rr):
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
    def niss_score(self, insult_dict):
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
    def return_triage_values(self, insults_dict, vitals_dict):

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
            niss_score = self.niss_score(insult_dict=insults_dict)
            if niss_score > 75:
                niss_score = 75
            final_score = round(niss_score/75,2)
        if not pd.isna(gcs) and not pd.isna(sbp) and not pd.isna(rr):
            normalized_gcs = self.get_normalized_gcs(gcs)
            normalized_sbp = self.get_normalized_sbp(sbp)
            normalized_rr = self.get_normalized_rr(rr)
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

        elif final_score >0.7:
            triage_category = 'immediate'
            lsi_hrs = 1.5
            rtd_hrs = 2160
            resource_required = 4

        return final_score, triage_category, lsi_hrs, rtd_hrs, resource_required







    def return_final_assignments_single_obj_scheduler(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list):

        terminate = False
        mission_final_assets = []
        schedule_dict = {}
        assets_schedule_start_timesteps = {}
        '''
        0.1: Compute triage score, triage category, lsi_ts, rtd_ts, resources_requirede
        0. Create pyreaon graph
        while not terminate:
             1. Create LP to frame optimization problems. (i/p: patients, assets, cfs, optimization criterions, (constraints, thresholds)), (o/p: dict_optimization instances)
             2. Run optimization instances (i/p: dict_optimization instances)(o/p: Results of optimization problems)


        '''
        for index, mission in enumerate(missions_options):
            insults_dict = mission.insults_dict
            vitals_dict = mission.vitals_dict
            triage_score, triage_category, lsi_ts, rtd_ts, equipments_needed = self.return_triage_values(insults_dict=insults_dict, vitals_dict=vitals_dict)
            mission.triage_score = triage_score
            mission.triage_category = triage_category
            mission.lsi_ts = lsi_ts
            mission.rtd_ts = rtd_ts
            mission.equipments_needed = equipments_needed







        self.initialize_pyreason(missions_options=missions_options, assets=assets, care_facilities=care_facilities, objectives=objectives)

        dict_optimization_instances = self.frame_opt_problems(missions_options=missions_options, assets=assets,
                                                              care_facilities=care_facilities)
        dict_optimization_results = self.run_optimization_instances(
            dict_optimization_instances=dict_optimization_instances)

        all_persons = dict_optimization_instances['persons']
        person_scores = dict_optimization_instances['person_score']
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_lsi_ts = dict_optimization_instances['person_lsi_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']
        # required_timesteps = dict_optimization_instances['required_timesteps']
        # required_distance = dict_optimization_instances['required_distance']
        # required_timesteps_lsi_only = dict_optimization_instances['required_timesteps_lsi_only']
        # required_timesteps_isop_cf = dict_optimization_instances['required_timesteps_isop_cf']


        solution_found = dict_optimization_results['solution_found']
        assignment_final = dict_optimization_results['assignment']
        print(assignment_final)


        if solution_found:
            for person, (asset, cf, ts) in assignment_final.items():
                mission_final_assets.append(
                    MissionFinalAssets(
                        patient_name=person,
                        datetime_seconds=int(datetime.now().timestamp()),
                        algo_name='pyreason_triage',
                        asset_final=asset,
                        asset_details=None,
                        confidence=1.0,
                        rationale=None,
                        interaction=None
                    )
                )


        # before finding all saved casualties
        curr_asset_location = dict_optimization_instances['curr_asset_location']
        assets_time_ranges = dict_optimization_instances['assets_time_ranges']
        assets_crew_duty_hrs = dict_optimization_instances['assets_crew_duty_hrs']
        all_lats_longs = dict_optimization_instances['all_lats_longs']
        all_assets = dict_optimization_instances['all_assets']
        all_cfs = dict_optimization_instances['all_cfs']
        assets_speeds = dict_optimization_instances['assets_speeds']
        person_score = dict_optimization_instances['person_score']
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']
        persons = all_persons.copy()

        for asset in all_assets:
            assets_schedule_start_timesteps[asset] =  0

        for person, (asset, cf, ts) in assignment_final.items():
            if person not in persons:
                continue
            schedule_dict[(asset, curr_asset_location[asset], person, cf)] = (0, ts)
            assets_schedule_start_timesteps[asset] = ts+1
            assets_time_ranges[asset] -= ts
            assets_crew_duty_hrs[asset] -= ts
            persons.remove(person)
            curr_asset_location[asset] = cf
        # Lets now iterate for rest of the schedule
        count_iterations = 0
        while (not terminate):
            required_timesteps = {}
            required_timesteps_lsi_only = {}
            required_distance = {}
            required_timesteps_isop_cf = {}
            assignment = {}


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
                        asset_person_d = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                                 person_long)
                        asset_person_t = asset_person_d / assets_speeds[asset]
                        person_cf_d = self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                        person_cf_t = person_cf_d / assets_speeds[asset]
                        trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                                person_long) + self.haversine_distance(person_lat,
                                                                                                       person_long,
                                                                                                       cf_lat,
                                                                                                       cf_lon)
                        trip_time = trip_distance / assets_speeds[asset]
                        required_timesteps[(person, asset, cf)] = trip_time + assets_schedule_start_timesteps[asset]
                        required_timesteps_lsi_only[(person, asset, cf)] = asset_person_t + assets_schedule_start_timesteps[asset]
                        # required_distance[(person, asset, cf)] = trip_distance
                        required_timesteps_isop_cf[(person, cf)] = person_cf_t
                        # if trip_time <= assets_time_ranges[asset] and trip_time <= assets_crew_duty_hrs[asset]:
                        #     required_timesteps[(person, asset, cf)] = trip_time
            print(required_timesteps)
            # Get schedul;e iteration 1
            if objectives[0] == 'PRIMARY':
                assignment = self.use_milp_primary_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score,
                    required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts)
            elif objectives[0] == 'REVERSE':
                assignment = self.use_milp_reverse_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs, rtd_timesteps=person_rtd_ts,
                    required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts)
            elif objectives[0] == 'SITUATIONAL':
                assignment = self.use_milp_situational_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs,
                    person_equipments_needed=person_equipments_needed, required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only,
                    person_lsi_ts=person_lsi_ts)

            # assignment_final.update(assignment)
            for person, (asset, cf, ts) in assignment.items():
                if person not in persons:
                    continue
                schedule_dict[(asset, curr_asset_location[asset], person, cf)] = (
                assets_schedule_start_timesteps[asset], ts)
                assets_schedule_start_timesteps[asset] = ts + 1
                assets_time_ranges[asset] -= ts
                curr_asset_location[asset] = cf
                persons.remove(person)
            count_iterations += 1
            if len(persons) == 0 or count_iterations > 10:
                terminate = True
        print(person_lsi_ts)
        for (asset, curr_asset_loc, person, cf), (start_time, end_time) in schedule_dict.items():
            print((asset, curr_asset_loc, person, cf), '----> ', (start_time, end_time))

        # after finding all saved casualties

        survived_casualties = [casualty for (_, _, casualty, _), val in schedule_dict.items()]
        non_survived_casualties = [cas for cas in all_persons if cas not in survived_casualties]

        if len(non_survived_casualties) > 0:
            terminate = False
        else:
            terminate = True

        # assigned_asset_cf = {casualty: (asset, cf) for (asset, _, casualty, cf), val in schedule_dict.items()}
        # assigned_ts = {casualty: (start_ts, end_ts) for (asset, _, casualty, cf), (start_ts, end_ts) in schedule_dict.items()}


        persons = non_survived_casualties.copy()

        # Lets now iterate for rest of the schedule
        while (not terminate):
            # print('First ioteration')
            required_timesteps = {}
            required_distance = {}
            required_timesteps_lsi_only ={}
            required_timesteps_isop_cf = {}


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
                        asset_person_d = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                                 person_long)
                        asset_person_t = asset_person_d / assets_speeds[asset]
                        person_cf_d = self.haversine_distance(person_lat,person_long,cf_lat,cf_lon)
                        person_cf_t = person_cf_d/assets_speeds[asset]
                        trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                                person_long) + self.haversine_distance(person_lat,
                                                                                                       person_long,
                                                                                                       cf_lat,
                                                                                                       cf_lon)
                        trip_time = trip_distance / assets_speeds[asset]
                        required_timesteps[(person, asset, cf)] = trip_time + assets_schedule_start_timesteps[asset]
                        required_timesteps_lsi_only[(person, asset, cf)] = asset_person_t + assets_schedule_start_timesteps[asset]
                        required_distance[(person, asset, cf)] = trip_distance
                        required_timesteps_isop_cf[(person, cf)] = person_cf_t


                        # if trip_time <= assets_time_ranges[asset] and trip_time <= assets_crew_duty_hrs[asset]:
                        #     required_timesteps[(person, asset, cf)] = trip_time
            print(required_timesteps)
            print(required_timesteps_lsi_only)
            print(persons)
            print(all_assets)
            print(all_cfs)
            print(person_lsi_ts)
            # Get schedul;e iteration 1
            if objectives[0] == 'PRIMARY':
                assignment = self.use_milp_primary_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score,
                    required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts, constraint_lsi = False)
            elif objectives[0] == 'REVERSE':
                assignment = self.use_milp_reverse_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs, rtd_timesteps=person_rtd_ts,
                    required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only, person_lsi_ts=person_lsi_ts, constraint_lsi = False)
            elif objectives[0] == 'SITUATIONAL':
                assignment = self.use_milp_situational_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs,
                    person_equipments_needed=person_equipments_needed, required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only,
                    person_lsi_ts=person_lsi_ts, constraint_lsi = False)

            # assignment_final.update(assignment)
            for person, (asset, cf, ts) in assignment.items():
                if person not in persons:
                    continue
                schedule_dict[(asset, curr_asset_location[asset], person, cf)] = (
                    assets_schedule_start_timesteps[asset], ts)
                assets_schedule_start_timesteps[asset] = ts + 1
                assets_time_ranges[asset] -= ts
                curr_asset_location[asset] = cf
                persons.remove(person)
            count_iterations += 1
            if len(persons) == 0 or count_iterations > 10:
                terminate = True
        print(person_lsi_ts)
        print('After survived ones')
        for (asset, curr_asset_location, person, cf), (start_time, end_time) in schedule_dict.items():
            print((asset, curr_asset_location, person, cf), '----> ', (start_time, end_time))

        columns = [
            'MEDEVAC Asset', 'Isolated Personnel', 'MEDEVAC Priority',
            'Route Distance (km)', 'Average Speed (km/hr)', 'Available Range', 'Time(min): Asset loc to isop loc', 'Time(min): isop loc to CF loc', 'Ground time',
            'Total trip time (min)', 'Medical Triage Category', 'Medical Triage Score', 'Need Life Saving Intervention in: (min)',
            'Forecasted Survival Status', 'Return to Duty in: (days)',
            'Resource Requirement'
        ]
        df = pd.DataFrame(columns=columns)

        # Sort the dictionary by values in descending order
        sorted_scores = sorted(person_scores.items(), key=lambda item: item[1], reverse=True)

        # Create a new dictionary for medevac priority
        medevac_priority_dict = {person: priority + 1 for priority, (person, _) in enumerate(sorted_scores)}

        for (chosen_asset, asset_start_loc, chosen_casualty, chosen_cf),(start_ts, end_ts) in schedule_dict.items():
            assigned_asset = None
            assigned_isop = None
            medevac_priority = None
            route_distance_km = None
            average_speed_kmph = None
            available_range_km = None
            asset_loc_to_isop_loc_time = None
            ground_time = None
            isop_loc_to_cf_loc_time = None
            total_trip_time_min = None
            triage_category = None
            triage_score = None
            lsi = None
            survival_status = None
            rtd = None
            resource = None

            assigned_asset = chosen_asset
            assigned_isop = chosen_casualty
            medevac_priority = medevac_priority_dict[chosen_casualty]

            person_lat = all_lats_longs[chosen_casualty][0]
            person_long = all_lats_longs[chosen_casualty][1]
            source_location = asset_start_loc
            asset_lat = all_lats_longs[source_location][0]
            asset_long = all_lats_longs[source_location][1]
            cf_lat = all_lats_longs[chosen_cf][0]
            cf_lon = all_lats_longs[chosen_cf][1]
            asset_person_d = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                     person_long)
            asset_person_t = asset_person_d / assets_speeds[chosen_asset]
            person_cf_d = self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
            person_cf_t = person_cf_d / assets_speeds[chosen_asset]
            route_distance_km = asset_person_d + person_cf_d

            for asset in assets:
                asset_record = asset.specifications_record
                if asset_record['asset_name'] == assigned_asset:
                    average_speed_kmph = asset_record['asset_speed_kmph']
                    available_range_km = asset_record['asset_range_in_km']

            asset_loc_to_isop_loc_time = round((start_ts + asset_person_t)*60,2)
            ground_time = 1
            isop_loc_to_cf_loc_time = round(person_cf_t*60,2)
            total_trip_time_min = round(end_ts*60,2)


            for mission in missions_options:
                if mission.patient_name == chosen_casualty:
                    triage_category = mission.triage_category
                    triage_score = mission.triage_score
                    lsi = round(mission.lsi_ts * 60, 2)
                    rtd = round(mission.rtd_ts / 24, 2)
                    resource = mission.equipments_needed
            survival_status = round(lsi - asset_loc_to_isop_loc_time,2)



            row1 = pd.DataFrame([{

                'MEDEVAC Asset': assigned_asset,
                'Isolated Personnel': assigned_isop,
                'MEDEVAC Priority': medevac_priority,
                'Route Distance (km)': route_distance_km,
                'Average Speed (km/hr)': average_speed_kmph,
                'Available Range': available_range_km,
                'Time(min): Asset loc to isop loc': asset_loc_to_isop_loc_time,
                'Time(min): isop loc to CF loc': isop_loc_to_cf_loc_time,
                'Ground time': ground_time,
                'Total trip time (min)': total_trip_time_min,
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
        csv_file_path = f'sample_single_obj_scheduler_{objectives[0]}.csv'

        # Append the DataFrame to the CSV file
        df.to_csv(csv_file_path, mode='w', header=True, index=True)


        return mission_final_assets, solution_found, schedule_dict, all_persons, person_scores, person_lsi_ts, person_rtd_ts, person_equipments_needed, required_timesteps
