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
import matplotlib.pyplot as plt
class OptimizationMultipleObjScheduler(OptimizationMethods):

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

        # m.objective = maximize(xsum(
        #     Y[p] * person_score[p] - 0.1 * Z[r, p, h] * required_timesteps[(p, r, h)] for p in persons for r in assets
        #     for h in hospitals if (p, r, h) in required_timesteps))
        m.objective = maximize(xsum(
            Y[p] + Y[p] * person_score[p] for p in persons) + xsum((1/(1+ required_timesteps[(p, r, h)])) * Z[r, p, h] for p in persons for r in assets
            for h in hospitals if (p, r, h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1


        # Optimize the model
        # m.optimize()
        # Optimize the model
        status = m.optimize()
        feasible_solution = status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE
        # Check if a solution was found
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print("Solution found:")
            for p in persons:
                print(f"Y[{p}] = {Y[p].x}")
                for r in assets:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps and Z[r,p,h].x > 0.99:  # Check if X[p, a, r] is set to 1
                            print(f"X[{r}, {p}, {h}] = 1 (assigned)")
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

        obj_value = None
        if m.num_solutions>0:
            print(f"Optimal objective value: {m.objective_value}")
            obj_value = m.objective_value

        return feasible_solution, assignment, obj_value, Z, Y

    def use_milp_reverse_triage(self, persons, assets, hospitals, required_timesteps, rtd_timesteps):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(
            Y[p] + Y[p] * (1 / (1 + rtd_timesteps[p])) for p in persons) +xsum((1/(1+ required_timesteps[(p, r, h)])) * Z[r, p, h] for p in persons for r in assets
            for h in hospitals if (p, r, h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1


        # Optimize the model
        # m.optimize()
        # Optimize the model
        status = m.optimize()
        feasible_solution = status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE
        # Check if a solution was found
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print("Solution found:")
            for p in persons:
                print(f"Y[{p}] = {Y[p].x}")
                for r in assets:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps and Z[r, p, h].x > 0.99:  # Check if X[p, a, r] is set to 1
                            print(f"X[{r}, {p}, {h}] = 1 (assigned)")
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

        obj_value = None
        if m.num_solutions>0:
            print(f"Optimal objective value: {m.objective_value}")
            obj_value = m.objective_value

        return feasible_solution, assignment, obj_value, Z, Y

    def use_milp_situational_triage(self, persons, assets, hospitals, required_timesteps,
                                    person_equipments_needed):
        # Create a new model
        m = Model()

        # Decision variables
        Z = {}
        for (p, r, h), _ in required_timesteps.items():
            Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

        Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

        m.objective = maximize(xsum(
            Y[p] + Y[p] * person_equipments_needed[p] for p in persons) + xsum((1/(1+ required_timesteps[(p, r, h)])) * Z[r, p, h] for p in persons for r in assets
            for h in hospitals if (p, r, h) in required_timesteps))

        # Constraints
        # Each person can be served by only one asset and transported to one hospital
        for p in persons:
            m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

        # Each asset can serve at most one person at a time
        for r in assets:
            m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1

        # Optimize the model
        # m.optimize()
        # Optimize the model
        status = m.optimize()
        feasible_solution = status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE
        # Check if a solution was found
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print("Solution found:")
            for p in persons:
                print(f"Y[{p}] = {Y[p].x}")
                for r in assets:
                    for h in hospitals:
                        if (p, r, h) in required_timesteps and Z[r, p, h].x > 0.99:  # Check if X[p, a, r] is set to 1
                            print(f"X[{r}, {p}, {h}] = 1 (assigned)")
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
        obj_value = None
        if m.num_solutions>0:
            print(f"Optimal objective value: {m.objective_value}")
            obj_value = m.objective_value

        return feasible_solution, assignment, obj_value, Z, Y

    def run_primary_objective(self, Z, Y, persons, assets, hospitals, person_score, required_timesteps):
        obj_val = 0
        for p in persons:
            obj_val += 1*Y[p] + 1*Y[p].x * person_score[p]
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps:

                        obj_val +=(1/(1+ required_timesteps[(p, r, h)]))*Z[r, p, h]
        # if float(obj_val) < 0:
        #     return 0
        return float(obj_val)

    def run_reverse_objective(self, Z, Y, persons, assets, hospitals, rtd_timesteps, required_timesteps):

        obj_val = 0
        for p in persons:
            obj_val += 1*Y[p] + 1*Y[p].x * (1 / (1 + rtd_timesteps[p]))
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps:

                        obj_val +=(1/(1+ required_timesteps[(p, r, h)]))*Z[r, p, h]
        # if float(obj_val) < 0:
        #     return 0
        return float(obj_val)

    def run_situational_objective(self, Z, Y, persons, assets, hospitals, person_equipments_needed, required_timesteps):
        obj_val = 0
        for p in persons:
            obj_val += 1*Y[p] + 1*Y[p].x * person_equipments_needed[p]
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps:

                        obj_val +=(1/(1+ required_timesteps[(p, r, h)]))*Z[r, p, h]
        # if float(obj_val)<0:
        #     return 0
        return float(obj_val)
    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'
    def create_pyreason_graph(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities: list[CareFacility], objectives: list):

        g = nx.DiGraph()
        primary_triage = True if 'PRIMARY' in objectives else False
        reverse_triage = True if 'REVERSE' in objectives else False
        situational_triage = True if 'SITUATIONAL' in objectives else False



        if primary_triage:
            g.add_node('PRIMARY', use_opt='1,1', type_primary = '1,1')
        else:
            g.add_node('PRIMARY', use_opt='0,0', type_primary = '1,1')

        if reverse_triage:
            g.add_node('REVERSE', use_opt='1,1', type_reverse = '1,1')
        else:
            g.add_node('REVERSE', use_opt='0,0', type_reverse = '1,1')
        if situational_triage:
            g.add_node('SITUATIONAL', use_opt='1,1', type_situational = '1,1')
        else:
            g.add_node('SITUATIONAL', use_opt='0,0', type_situational = '1,1')
        g.add_node('None', type_none = '1,1')

        g.add_node('final_solution', solution_found='0,1', type_final_solution = '1,1', select_primary_solution='0,1', select_reverse_triage='0,1', select_situational_triage='0,1')

        solution_possibilities = ['PRIMARY', 'REVERSE', 'SITUATIONAL', 'None']
        for sol in solution_possibilities:
            g.add_edge('final_solution', sol, accept_possible = '0,1', accept_final = '0,1')





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
                g.add_edge(asset_name, patient_name, assign_asset_primary_triage='0,1', assign_asset_reverse_triage='0,1', assign_asset_situational_triage='0,1', assign_final_asset='0,1')
            for index2, cf in enumerate(care_facilities):
                record = cf.specifications_record
                cf_name = record['cf_name']
                g.add_edge(cf_name, patient_name, assign_cf_primary_triage='0,1', assign_cf_reverse_triage='0,1', assign_cf_situational_triage='0,1', assign_final_cf = '0,1')



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
    def get_casualties_dicts(self, missions_options, persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs):

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

            person_score[patient_name] = 1-(patient_triage_score/100)
            person_ts_available[patient_name] = patient_ts_available
            person_rtd_ts[patient_name] =patient_rtd_ts
            person_equipments_needed[patient_name] = patient_equipments_needed

            all_lats_longs[patient_name] = patient_location

        return persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs
    def get_assets_dicts(self, assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs):
        all_assets = []
        for index, asset in enumerate(assets):
            record = asset.specifications_record
            asset_name = record['asset_name']
            asset_range_in_km = record['asset_range_in_km']
            asset_speed_kmph = record['asset_speed_kmph']
            asset_time_range = asset_range_in_km/asset_speed_kmph
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

    def get_required_timestamps_dict(self, persons, all_assets, all_cfs, all_lats_longs, curr_asset_location, assets_crew_duty_hrs, assets_speeds, assets_time_ranges):
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
                    trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat, person_long) + self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                    trip_time = trip_distance/assets_speeds[asset]

                    if trip_time <= assets_time_ranges[asset] and trip_time < crew_duty_hrs:
                        required_timesteps[(person, asset, cf)] = trip_time
        return required_timesteps
    def run_opt_problems(self, persons:list, all_assets:list, all_cfs, person_score:dict, required_timesteps:dict, person_rtd_ts:dict, person_equipments_needed:dict, run_primary: bool, run_reverse: bool, run_situational: bool):

        primary_feasible, assignment_primary, primary_obj_val, Z_primary, Y_primary = None, None, None, None, None
        reverse_feasible, assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse = None, None, None, None, None
        situational_feasible, assignment_situational, situational_obj_val, Z_situational, Y_situational = None, None, None, None, None

        if run_primary:
            primary_feasible, assignment_primary, primary_obj_val, Z_primary, Y_primary = self.use_milp_primary_triage(persons= persons, assets= all_assets, hospitals= all_cfs, person_score= person_score, required_timesteps= required_timesteps)
        if run_reverse:
            reverse_feasible, assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse = self.use_milp_reverse_triage(persons=persons, assets=all_assets, hospitals=all_cfs, rtd_timesteps= person_rtd_ts, required_timesteps= required_timesteps)
        if run_situational:
            situational_feasible, assignment_situational, situational_obj_val, Z_situational, Y_situational = self.use_milp_situational_triage(persons=persons, assets=all_assets, hospitals=all_cfs, person_equipments_needed=person_equipments_needed, required_timesteps=required_timesteps)

        return (primary_feasible, assignment_primary, primary_obj_val, Z_primary, Y_primary), (reverse_feasible, assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse), (situational_feasible, assignment_situational, situational_obj_val, Z_situational, Y_situational)

    def is_acceptable_solution(self, best_value, query_value):
        percentage = 10
        tolerance = (percentage / 100) * best_value
        lower_bound = best_value - tolerance
        return query_value >= lower_bound
    def gap_acceptable_solution(self, best_value, query_value):

        return best_value-query_value
    def plot_radar_chart(self, data, accepted):


        # Input values
        criteria = ['Primary', 'Reverse', 'Situational']


        # Normalize the data
        max_values = data['Theoretical best']
        normalized_data = {}
        for label, d in data.items():
            normalized_data[label] = [d[i] / max_values[i] for i in range(len(d))]

        # Number of variables we're plotting.
        num_vars = len(criteria)

        # Split the circle into even parts and save the angles
        # so we know where to put each axis.
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # The radar chart is a circle, so we need to "complete the loop"
        # and append the start value to the end.
        angles += angles[:1]

        # Create the figure and the polar subplot.
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))  # Increase figure size

        del normalized_data['Theoretical best']
        # Plot each individual data set.
        for label, d in normalized_data.items():
            values = d + d[:1]
            ax.plot(angles, values, label=label)
            ax.fill(angles, values, alpha=0.25)

        # Set y-ticks to create 20 equally spaced circles
        num_circles = 10
        ax.set_yticks([i / num_circles for i in range(num_circles + 1)])
        ax.set_yticklabels([f'{int(10 * i)}%' for i in range(num_circles + 1)])

        # Labels for each point.
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(criteria, va='center', ha='left')

        # Ensure the outermost circle represents the maximum value for each axis
        ax.set_ylim(0, 1)

        # Title and legend.
        plt.title(f'Chosen solution: {accepted}', size=20, color='black', y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.05))  # Adjust legend position

        plt.tight_layout()  # Automatically adjust subplot parameters for padding

        # Save the figure
        plt.savefig('radar_chart.png', dpi=300, bbox_inches='tight')  # Save as PNG with high resolution

        plt.show()

    def check_criterion(self, best_obj_val, accepted_list, primary_sol, reverse_sol, situational_sol):

        final_accepted_list = accepted_list.copy()
        for triage in accepted_list:
            if triage == 'PRIMARY':
                # print(best_obj_val, primary_sol)
                accepted = self.is_acceptable_solution(best_value=best_obj_val, query_value=primary_sol)
                if not accepted:
                    final_accepted_list.remove('PRIMARY')
            if triage == 'REVERSE':
                accepted = self.is_acceptable_solution(best_value=best_obj_val, query_value=reverse_sol)
                if not accepted:
                    final_accepted_list.remove('REVERSE')
            if triage == 'SITUATIONAL':
                accepted = self.is_acceptable_solution(best_value=best_obj_val, query_value=situational_sol)
                if not accepted:
                    final_accepted_list.remove('SITUATIONAL')
        return final_accepted_list
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
        graphml_path = 'pyreason_input_graph_mission_assets_triage_types.graphml'
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
        folder_name = 'traces_t0_triage_types'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

    def frame_opt_problems(self, missions_options, assets, care_facilities, objectives):

        dict_optimization_instances = {}

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
        assets_speeds = {}
        assets_time_ranges = {}
        assets_crew_duty_hrs = {}

        persons, person_score, person_ts_available, person_rtd_ts, person_equipments_needed, all_lats_longs = self.get_casualties_dicts(
            missions_options=missions_options, persons=persons, person_score=person_score,
            person_ts_available=person_ts_available, person_rtd_ts=person_rtd_ts,
            person_equipments_needed=person_equipments_needed, all_lats_longs=all_lats_longs)
        all_assets, assets_time_ranges, curr_asset_location, assets_speeds, all_lats_longs, assets_crew_duty_hrs = self.get_assets_dicts(
            assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location, assets_speeds=assets_speeds,
            all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)

        all_cfs, all_lats_longs = self.get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

        required_timesteps = self.get_required_timestamps_dict(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
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
        folder_name = 'traces_t1_triage_types'
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
        dict_optimization_instances['person_rtd_ts'] = person_rtd_ts
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
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']
        run_primary_triage = dict_optimization_instances['run_primary_triage']
        run_reverse_triage = dict_optimization_instances['run_reverse_triage']
        run_situational_triage = dict_optimization_instances['run_situational_triage']

        (primary_feasible, assignment_primary, primary_obj_val, Z_primary, Y_primary), (
        reverse_feasible, assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse), (
        situational_feasible, assignment_situational, situational_obj_val, Z_situational,
        Y_situational) = self.run_opt_problems(persons=persons, all_assets=all_assets, all_cfs=all_cfs,
                                               person_score=person_score, required_timesteps=required_timesteps,
                                               person_rtd_ts=person_rtd_ts,
                                               person_equipments_needed=person_equipments_needed, run_primary=run_primary_triage,
                                               run_reverse=run_reverse_triage, run_situational=run_situational_triage
                                               )
        dict_optimization_results['assignment_primary'] = assignment_primary
        dict_optimization_results['assignment_reverse'] = assignment_reverse
        dict_optimization_results['assignment_situational'] = assignment_situational
        dict_optimization_results['primary_obj_val'] = primary_obj_val
        dict_optimization_results['reverse_obj_val'] = reverse_obj_val
        dict_optimization_results['situational_obj_val'] = situational_obj_val
        dict_optimization_results['primary_feasible'] = primary_feasible
        dict_optimization_results['reverse_feasible'] = reverse_feasible
        dict_optimization_results['situational_feasible'] = situational_feasible
        if not (primary_feasible and reverse_feasible and situational_feasible):
            dict_optimization_results['solution_found'] = False
            ((primary_sol_primary_obj, reverse_sol_primary_obj, situational_sol_primary_obj),
             (primary_sol_reverse_obj, reverse_sol_reverse_obj, situational_sol_reverse_obj),
             (primary_sol_situational_obj, reverse_sol_situational_obj, situational_sol_situational_obj)) = (
                (None, None, None), (None, None, None), (None, None, None))
            dict_optimization_results['primary_sol_primary_obj'] = primary_sol_primary_obj
            dict_optimization_results['primary_sol_reverse_obj'] = primary_sol_reverse_obj
            dict_optimization_results['primary_sol_situational_obj'] = primary_sol_situational_obj
            dict_optimization_results['reverse_sol_reverse_obj'] = reverse_sol_reverse_obj
            dict_optimization_results['reverse_sol_situational_obj'] = reverse_sol_situational_obj
            dict_optimization_results['reverse_sol_primary_obj'] = reverse_sol_primary_obj
            dict_optimization_results['situational_sol_primary_obj'] = situational_sol_primary_obj
            dict_optimization_results['situational_sol_reverse_obj'] = situational_sol_reverse_obj
            dict_optimization_results['situational_sol_situational_obj'] = situational_sol_situational_obj
            return dict_optimization_results
        else:
            solution_found = True



            primary_sol_primary_obj = self.run_primary_objective(Z=Z_primary, Y=Y_primary, persons=persons,
                                                                 assets=all_assets, hospitals=all_cfs,
                                                                 person_score=person_score,
                                                                 required_timesteps=required_timesteps)
            primary_sol_reverse_obj = self.run_reverse_objective(Z=Z_primary, Y=Y_primary, persons=persons,
                                                                 assets=all_assets, hospitals=all_cfs,
                                                                 rtd_timesteps=person_rtd_ts,
                                                                 required_timesteps=required_timesteps)
            primary_sol_situational_obj = self.run_situational_objective(Z=Z_primary, Y=Y_primary, persons=persons,
                                                                         assets=all_assets, hospitals=all_cfs,
                                                                         person_equipments_needed=person_equipments_needed,
                                                                         required_timesteps=required_timesteps)

            reverse_sol_primary_obj = self.run_primary_objective(Z=Z_reverse, Y=Y_reverse, persons=persons,
                                                                 assets=all_assets, hospitals=all_cfs,
                                                                 person_score=person_score,
                                                                 required_timesteps=required_timesteps)
            reverse_sol_reverse_obj = self.run_reverse_objective(Z=Z_reverse, Y=Y_reverse, persons=persons,
                                                                 assets=all_assets, hospitals=all_cfs,
                                                                 rtd_timesteps=person_rtd_ts,
                                                                 required_timesteps=required_timesteps)
            reverse_sol_situational_obj = self.run_situational_objective(Z=Z_reverse, Y=Y_reverse, persons=persons,
                                                                         assets=all_assets, hospitals=all_cfs,
                                                                         person_equipments_needed=person_equipments_needed,
                                                                         required_timesteps=required_timesteps)

            situational_sol_primary_obj = self.run_primary_objective(Z=Z_situational, Y=Y_situational, persons=persons,
                                                                     assets=all_assets, hospitals=all_cfs,
                                                                     person_score=person_score,
                                                                     required_timesteps=required_timesteps)
            situational_sol_reverse_obj = self.run_reverse_objective(Z=Z_situational, Y=Y_situational, persons=persons,
                                                                     assets=all_assets, hospitals=all_cfs,
                                                                     rtd_timesteps=person_rtd_ts,
                                                                     required_timesteps=required_timesteps)
            situational_sol_situational_obj = self.run_situational_objective(Z=Z_situational, Y=Y_situational,
                                                                             persons=persons, assets=all_assets,
                                                                             hospitals=all_cfs,
                                                                             person_equipments_needed=person_equipments_needed,
                                                                             required_timesteps=required_timesteps)


            dict_optimization_results['primary_sol_primary_obj'] = primary_sol_primary_obj
            dict_optimization_results['primary_sol_reverse_obj'] = primary_sol_reverse_obj
            dict_optimization_results['primary_sol_situational_obj'] = primary_sol_situational_obj
            dict_optimization_results['reverse_sol_reverse_obj'] = reverse_sol_reverse_obj
            dict_optimization_results['reverse_sol_situational_obj'] = reverse_sol_situational_obj
            dict_optimization_results['reverse_sol_primary_obj'] = reverse_sol_primary_obj
            dict_optimization_results['situational_sol_primary_obj'] = situational_sol_primary_obj
            dict_optimization_results['situational_sol_reverse_obj'] = situational_sol_reverse_obj
            dict_optimization_results['situational_sol_situational_obj'] = situational_sol_situational_obj


            dict_optimization_results['solution_found'] = solution_found

            return dict_optimization_results


    def run_final_lp(self, dict_optimization_results, num_iterations):
        primary_feasible = dict_optimization_results['primary_feasible']
        reverse_feasible = dict_optimization_results['reverse_feasible']
        situational_feasible = dict_optimization_results['situational_feasible']
        accepted_list_1 = []
        accepted_list_2 = []
        accepted_list_3 = []
        accepted = 'None'
        if primary_feasible and reverse_feasible and situational_feasible:
            primary_obj_val = dict_optimization_results['primary_obj_val']
            reverse_obj_val = dict_optimization_results['reverse_obj_val']
            situational_obj_val = dict_optimization_results['situational_obj_val']
            primary_sol_primary_obj = dict_optimization_results['primary_sol_primary_obj']
            primary_sol_reverse_obj = dict_optimization_results['primary_sol_reverse_obj']
            primary_sol_situational_obj = dict_optimization_results['primary_sol_situational_obj']
            reverse_sol_reverse_obj = dict_optimization_results['reverse_sol_reverse_obj']
            reverse_sol_situational_obj = dict_optimization_results['reverse_sol_situational_obj']
            reverse_sol_primary_obj = dict_optimization_results['reverse_sol_primary_obj']
            situational_sol_primary_obj = dict_optimization_results['situational_sol_primary_obj']
            situational_sol_reverse_obj = dict_optimization_results['situational_sol_reverse_obj']
            situational_sol_situational_obj = dict_optimization_results['situational_sol_situational_obj']
            accepted_list = ['PRIMARY', 'REVERSE', 'SITUATIONAL']
            accepted_list_1 = self.check_criterion(best_obj_val=primary_obj_val, accepted_list=accepted_list,
                                                   primary_sol=primary_sol_primary_obj,
                                                   reverse_sol=reverse_sol_primary_obj,
                                                   situational_sol=situational_sol_primary_obj)
            accepted_list_1.remove('PRIMARY')
            print(accepted_list_1)

            accepted_list_2 = self.check_criterion(best_obj_val=reverse_obj_val, accepted_list=accepted_list,
                                                   primary_sol=primary_sol_reverse_obj,
                                                   reverse_sol=reverse_sol_reverse_obj,
                                                   situational_sol=situational_sol_reverse_obj)
            accepted_list_2.remove('REVERSE')
            print(accepted_list_2)

            accepted_list_3 = self.check_criterion(best_obj_val=situational_obj_val,
                                                   accepted_list=accepted_list,
                                                   primary_sol=primary_sol_situational_obj,
                                                   reverse_sol=reverse_sol_situational_obj,
                                                   situational_sol=situational_sol_situational_obj)
            accepted_list_3.remove('SITUATIONAL')
            print(accepted_list_3)

        edge_facts = []
        node_facts = []
        # accepted = 'None'
        primary_obj_not = set(['REVERSE', 'SITUATIONAL']).difference(accepted_list_1)
        reverse_obj_not = set(['PRIMARY', 'SITUATIONAL']).difference(accepted_list_2)
        situational_obj_not = set(['PRIMARY', 'REVERSE']).difference(accepted_list_3)
        fact = pr.fact_node.Fact(f'f_acc',
                                 'final_solution',
                                 pr.label.Label('primary_none'),
                                 pr.interval.closed(0, 0),
                                 self.next_time,
                                 self.next_time)
        node_facts.append(fact)
        fact = pr.fact_node.Fact(f'f_acc',
                                 'final_solution',
                                 pr.label.Label('reverse_none'),
                                 pr.interval.closed(0, 0),
                                 self.next_time,
                                 self.next_time)
        node_facts.append(fact)
        fact = pr.fact_node.Fact(f'f_acc',
                                 'final_solution',
                                 pr.label.Label('situational_none'),
                                 pr.interval.closed(0, 0),
                                 self.next_time,
                                 self.next_time)
        node_facts.append(fact)
        for acc in accepted_list_1:
            fact = pr.fact_node.Fact(f'f_acc',
                                     acc,
                                     pr.label.Label('accept_primary'),
                                     pr.interval.closed(1, 1),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)
        for accn in primary_obj_not:
            fact = pr.fact_node.Fact(f'f_accn',
                                     accn,
                                     pr.label.Label('accept_primary'),
                                     pr.interval.closed(0, 0),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)
        for acc in accepted_list_2:
            fact = pr.fact_node.Fact(f'f_acc',
                                     acc,
                                     pr.label.Label('accept_reverse'),
                                     pr.interval.closed(1, 1),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)
        for accn in reverse_obj_not:
            fact = pr.fact_node.Fact(f'f_accn',
                                     accn,
                                     pr.label.Label('accept_reverse'),
                                     pr.interval.closed(0, 0),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)
        for acc in accepted_list_3:
            fact = pr.fact_node.Fact(f'f_acc',
                                     acc,
                                     pr.label.Label('accept_situational'),
                                     pr.interval.closed(1, 1),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)
        for accn in situational_obj_not:
            fact = pr.fact_node.Fact(f'f_accn',
                                     accn,
                                     pr.label.Label('accept_situational'),
                                     pr.interval.closed(0, 0),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)



        # Reason at t=2
        self.interpretation = pr.reason(again=True, node_facts=node_facts, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t2_triage_types'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        field = 'accept_final'

        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        accepted = None
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        if df['component'][i][1]!='None':
                            accepted = df['component'][i][1]
                            print('Accepted = ', accepted)

        return accepted





    def return_final_assignments_multiple_obj_scheduler(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities : list[CareFacility], objectives: list):

        terminate = False
        mission_final_assets = []
        ((primary_sol_primary_obj, reverse_sol_primary_obj, situational_sol_primary_obj),
         (primary_sol_reverse_obj, reverse_sol_reverse_obj, situational_sol_reverse_obj),
         (primary_sol_situational_obj, reverse_sol_situational_obj, situational_sol_situational_obj)) = (
            (None, None, None), (None, None, None), (None, None, None))
        '''
        0. Create pyreaon graph
        while not terminate:
             1. Create LP to frame optimization problems. (i/p: patients, assets, cfs, optimization criterions, (constraints, thresholds)), (o/p: dict_optimization instances)
             2. Run optimization instances (i/p: dict_optimization instances)(o/p: Results of optimization problems)
             3. LP to decide next step i.e. (Solution found->terminate) or  (Solution not found->not terminate-> update constraint thresholds)
            
        
        '''

        self.initialize_pyreason(missions_options=missions_options, assets=assets, care_facilities= care_facilities, objectives= objectives)
        num_iterations = 0
        schedule_dict = {}

        # Iteration 1
        dict_optimization_instances = self.frame_opt_problems(missions_options=missions_options, assets=assets, care_facilities= care_facilities, objectives= objectives)
        curr_asset_location = dict_optimization_instances['curr_asset_location']
        assets_schedule_start_timesteps = {}
        assets_time_ranges = dict_optimization_instances['assets_time_ranges']
        persons = dict_optimization_instances['persons']
        all_lats_longs = dict_optimization_instances['all_lats_longs']
        all_assets = dict_optimization_instances['all_assets']
        all_cfs = dict_optimization_instances['all_cfs']
        assets_speeds = dict_optimization_instances['assets_speeds']
        person_score = dict_optimization_instances['person_score']
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']
        assets_crew_duty_hrs = dict_optimization_instances['assets_crew_duty_hrs']


        dict_optimization_results = self.run_optimization_instances(dict_optimization_instances = dict_optimization_instances)
        accepted = self.run_final_lp(dict_optimization_results=dict_optimization_results, num_iterations=num_iterations)





        num_iterations += 1
        if pd.isna(accepted):
            print('None')
            return mission_final_assets, num_iterations, 'None', schedule_dict
        else:
            print(accepted)
            if accepted == 'PRIMARY':
                assignment = dict_optimization_results['assignment_primary']
            elif accepted == 'REVERSE':
                assignment = dict_optimization_results['assignment_reverse']
            elif accepted == 'SITUATIONAL':
                assignment = dict_optimization_results['assignment_situational']

        for person, (asset, cf, ts) in assignment.items():
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
                        trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                                person_long) + self.haversine_distance(person_lat,
                                                                                                       person_long,
                                                                                                       cf_lat,
                                                                                                       cf_lon)
                        trip_time = trip_distance / assets_speeds[asset]
                        if trip_time <= assets_time_ranges[asset] and trip_time < assets_crew_duty_hrs[asset]:
                            required_timesteps[(person, asset, cf)] = trip_time

            # Get schedul;e iteration 1
            if accepted == 'PRIMARY':
                feasible_solution, assignment, obj_value, Z, Y = self.use_milp_primary_triage(persons=persons, assets=all_assets, hospitals=all_cfs, person_score=person_score, required_timesteps=required_timesteps)
            elif accepted == 'REVERSE':
                feasible_solution, assignment, obj_value, Z, Y = self.use_milp_reverse_triage(persons=persons, assets=all_assets, hospitals=all_cfs, required_timesteps=required_timesteps, rtd_timesteps=person_rtd_ts)
            elif accepted == 'SITUATIONAL':
                feasible_solution, assignment, obj_value, Z, Y = self.use_milp_situational_triage(persons=persons, assets=all_assets, hospitals=all_cfs, required_timesteps=required_timesteps, person_equipments_needed=person_equipments_needed)


            for person, (asset, cf, ts) in assignment.items():
                schedule_dict[(asset, curr_asset_location[asset], person, cf)] = (
                assets_schedule_start_timesteps[asset], assets_schedule_start_timesteps[asset] + ts)
                assets_schedule_start_timesteps[asset] = assets_schedule_start_timesteps[asset] + ts + 1
                assets_time_ranges[asset] -= ts
                curr_asset_location[asset] = cf
                persons.remove(person)
            count_iterations += 1
            if len(persons) == 0 or count_iterations > 10:
                terminate = True
        for (asset, curr_asset_location, person, cf), (start_time, end_time) in schedule_dict.items():
            print((asset, curr_asset_location, person, cf), '----> ', (start_time, end_time))



        return mission_final_assets, num_iterations, accepted, schedule_dict
