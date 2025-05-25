import pandas as pd
from services.service_medevac_planning.algos.algo_final_assignment.algo_multiple_obj.numba_annotation_functions import rts_ann_fn, niss_ann_fn,life_ann_fn, final_niss_ann_fn, final_rts_ann_fn
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility
from services.models.ModelPlan import Plan

from services.service_medevac_planning.algos.algo_final_assignment.algo_multiple_obj.optimization_functions import use_milp_urgency_triage, use_milp_reverse_triage

import networkx as nx
import pyreason as pr
import os
import math
class MedevacHelper:
    """
        A helper class for medical evacuation (MEDEVAC) planning and optimization.

        This class provides methods for framing optimization problems, running optimization instances,
        and handling various aspects of MEDEVAC optimization solutions using PyReason and Mixed Integer Linear Programming (MILP).

        Attributes:
            interpretation: The current PyReason interpretation.
            next_time: The next time step for PyReason reasoning.

        Methods:
            frame_opt_problems: Frames the optimization problems based on mission options(casualties), assets, and care facilities.
            run_opt_problems: Runs the optimization problems for urgency and reverse triage.
            run_optimization_instances: Executes optimization instances based on the framed problems.
            haversine_distance: Calculates the Haversine distance between two points on Earth.
            travel_time: Calculates the travel time between two points given a speed.
            get_casualties_dicts: Extracts casualty information from mission options.
            get_assets_dicts: Extracts asset information.
            get_cf_dicts: Extracts care facility information.
            get_required_timestamps_dict: Calculates required timestamps for various combinations.
            return_triage_values: Returns triage values based on a final score.
            write_graphml: Writes a NetworkX graph to a GraphML file.
            create_pyreason_graph: Creates a PyReason graph from mission options, assets, and care facilities.
            initialize_pyreason: Initializes PyReason with the created graph and rules.
            get_filtered_casualties_info: Filters and updates casualty information based on triage scores.
            get_final_assignments: Generates final assignments based on optimization results.

        The class integrates various components of MEDEVAC planning, including graph creation,
        PyReason initialization, optimization problem framing, and result processing.
        """
    def __init__(self):
        """
            Initialize the MedevacHelper instance.
        """
        self.interpretation = None
        self.next_time = 0

    def frame_opt_problems(self, missions_options, assets, care_facilities):
        """
                Frame optimization problems based on mission options, assets, and care facilities.

                Args:
                    missions_options (list): List of mission options.
                    assets (list): List of available assets.
                    care_facilities (list): List of care facilities.

                Returns:
                    dict: A dictionary containing optimization problem instances.
                """
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
            assets=assets, assets_time_ranges=assets_time_ranges, curr_asset_location=curr_asset_location,
            assets_speeds=assets_speeds,
            all_lats_longs=all_lats_longs, assets_crew_duty_hrs=assets_crew_duty_hrs)

        all_cfs, all_lats_longs = self.get_cf_dicts(care_facilities=care_facilities, all_lats_longs=all_lats_longs)

        required_timesteps, required_distance, required_timesteps_lsi_only, required_ts_asset_isop, required_ts_isop_cf = self.get_required_timestamps_dict(
            persons=persons, all_assets=all_assets, all_cfs=all_cfs,
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
        folder_name = 'traces_t1'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        run_urgency_triage = False
        run_reverse_triage = False
        field = 'run_opt'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        triage_type = df['component'][i]
                        if triage_type == 'urgency':
                            run_urgency_triage = True
                        if triage_type == 'reverse':
                            run_reverse_triage = True
        constraint_lsi = False
        constraint_air_time = False
        threshold_air = None
        field = 'use_constraint'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        constraint_type = df['component'][i]
                        if constraint_type == 'lsi':
                            constraint_lsi = True
                        if constraint_type == 'air_time':
                            constraint_air_time = True
                            field_inner = 'threshold'
                            df_inner = pr.filter_and_sort_edges(self.interpretation, [(field_inner)])
                            for t1, dft in enumerate(df_inner):
                                if not dft[field_inner].empty:
                                    for i in range(len(dft['component'])):
                                        if dft[field_inner][i] == [1, 1]:
                                            threshold_air = float(dft['component'][i][1])

        dict_optimization_instances['persons'] = persons
        dict_optimization_instances['all_assets'] = all_assets
        dict_optimization_instances['all_cfs'] = all_cfs
        dict_optimization_instances['person_score'] = person_score
        dict_optimization_instances['required_timesteps'] = required_timesteps
        dict_optimization_instances['required_timesteps_lsi_only'] = required_timesteps_lsi_only
        dict_optimization_instances['required_ts_asset_isop'] = required_ts_asset_isop
        dict_optimization_instances['required_ts_isop_cf'] = required_ts_isop_cf
        dict_optimization_instances['required_distance'] = required_distance
        dict_optimization_instances['person_rtd_ts'] = person_rtd_ts
        dict_optimization_instances['person_lsi_ts'] = person_lsi_ts
        dict_optimization_instances['person_equipments_needed'] = person_equipments_needed
        dict_optimization_instances['curr_asset_location'] = curr_asset_location
        dict_optimization_instances['assets_time_ranges'] = assets_time_ranges
        dict_optimization_instances['all_lats_longs'] = all_lats_longs
        dict_optimization_instances['assets_speeds'] = assets_speeds
        dict_optimization_instances['assets_crew_duty_hrs'] = assets_crew_duty_hrs
        dict_optimization_instances['run_urgency_triage'] = run_urgency_triage
        dict_optimization_instances['run_reverse_triage'] = run_reverse_triage
        dict_optimization_instances['constraint_lsi'] = constraint_lsi
        dict_optimization_instances['constraint_air_time'] = constraint_air_time
        dict_optimization_instances['threshold_air'] = threshold_air
        return dict_optimization_instances

    def run_opt_problems(self, persons: list, all_assets: list, all_cfs, person_score: dict, person_lsi_ts: dict,
                         required_timesteps: dict, required_timesteps_lsi_only: dict,
                         required_ts_asset_isop: dict, required_ts_isop_cf: dict,
                         person_rtd_ts: dict, person_equipments_needed: dict,
                         run_urgency: bool, run_reverse: bool,
                         constraint_lsi: bool,
                         constraint_air: bool,
                         threshold_air):

        """
                Run optimization problems for urgency and reverse triage.

                Args:
                    persons (list): List of persons to be evacuated.
                    all_assets (list): List of all available assets.
                    all_cfs: List of all care facilities.
                    person_score (dict): Dictionary of scores for each person.
                    person_lsi_ts (dict): Dictionary of LSI timestamps for each person.
                    required_timesteps (dict): Dictionary of required timesteps.
                    required_timesteps_lsi_only (dict): Dictionary of required timesteps for LSI only.
                    required_ts_asset_isop (dict): Dictionary of required timesteps from asset to ISOP.
                    required_ts_isop_cf (dict): Dictionary of required timesteps from ISOP to care facility.
                    person_rtd_ts (dict): Dictionary of RTD timestamps for each person.
                    person_equipments_needed (dict): Dictionary of equipment needed for each person.
                    run_urgency (bool): Whether to run urgency triage.
                    run_reverse (bool): Whether to run reverse triage.
                    constraint_lsi (bool): Whether to apply LSI constraints.
                    constraint_air (bool): Whether to apply air constraints.
                    threshold_air: Threshold for air constraints.

                Returns:
                    tuple: A tuple containing the results of urgency and reverse triage optimal solutions/assignments.
        """
        assignment_urgency, urgency_obj_val, Z_urgency, Y_urgency = None, None, None, None
        assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse = None, None, None, None

        if run_reverse:
            assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse = use_milp_reverse_triage(
                persons=persons, assets=all_assets, hospitals=all_cfs, rtd_timesteps=person_rtd_ts,
                required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only,
                person_lsi_ts=person_lsi_ts, required_ts_asset_isop=required_ts_asset_isop,
                required_ts_isop_cf=required_ts_isop_cf, constraint_lsi=constraint_lsi,
                constraint_air_time=constraint_air,
                threshold_air_time=threshold_air)
        if run_urgency:
            assignment_urgency, urgency_obj_val, Z_urgency, Y_urgency = use_milp_urgency_triage(persons=persons,
                                                                                                     assets=all_assets,
                                                                                                     hospitals=all_cfs,
                                                                                                     required_timesteps=required_timesteps,
                                                                                                     required_timesteps_lsi_only=required_timesteps_lsi_only,
                                                                                                     person_score=person_score,
                                                                                                     person_lsi_ts=person_lsi_ts,
                                                                                                     required_ts_asset_isop=required_ts_asset_isop,
                                                                                                     required_ts_isop_cf=required_ts_isop_cf,
                                                                                                     constraint_lsi=constraint_lsi,
                                                                                                     constraint_air_time=constraint_air,
                                                                                                     threshold_air_time=threshold_air)
        return (assignment_urgency, urgency_obj_val, Z_urgency, Y_urgency), (
            assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse)

    def run_optimization_instances(self, dict_optimization_instances):
        """
                Run optimization instances based on the framed problems.

                Args:
                    dict_optimization_instances (dict): Dictionary containing optimization problem instances.

                Returns:
                    dict: A dictionary containing optimization results.
                """
        dict_optimization_results = {}
        persons = dict_optimization_instances['persons']
        all_assets = dict_optimization_instances['all_assets']
        all_cfs = dict_optimization_instances['all_cfs']
        person_score = dict_optimization_instances['person_score']
        required_timesteps = dict_optimization_instances['required_timesteps']
        required_timesteps_lsi_only = dict_optimization_instances['required_timesteps_lsi_only']
        required_ts_asset_isop = dict_optimization_instances['required_ts_asset_isop']
        required_ts_isop_cf = dict_optimization_instances['required_ts_isop_cf']
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_lsi_ts = dict_optimization_instances['person_lsi_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']
        run_urgency_triage = dict_optimization_instances['run_urgency_triage']
        run_reverse_triage = dict_optimization_instances['run_reverse_triage']

        constraint_lsi = dict_optimization_instances['constraint_lsi']
        constraint_air_time = dict_optimization_instances['constraint_air_time']
        threshold_air = dict_optimization_instances['threshold_air']
        ((assignment_urgency, urgency_obj_val, Z_urgency, Y_urgency),
         (assignment_reverse, reverse_obj_val, Z_reverse, Y_reverse)) = self.run_opt_problems(persons=persons,
                                                                                              all_assets=all_assets,
                                                                                              all_cfs=all_cfs,
                                                                                              person_score=person_score,
                                                                                              required_timesteps=required_timesteps,
                                                                                              required_timesteps_lsi_only=required_timesteps_lsi_only,
                                                                                              required_ts_asset_isop=required_ts_asset_isop,
                                                                                              required_ts_isop_cf=required_ts_isop_cf,
                                                                                              person_rtd_ts=person_rtd_ts,
                                                                                              person_lsi_ts=person_lsi_ts,
                                                                                              person_equipments_needed=person_equipments_needed,
                                                                                              run_urgency=run_urgency_triage,
                                                                                              run_reverse=run_reverse_triage,
                                                                                              constraint_lsi=constraint_lsi,
                                                                                              constraint_air=constraint_air_time,
                                                                                              threshold_air=threshold_air
                                                                                              )
        dict_optimization_results['assignment_urgency'] = assignment_urgency
        dict_optimization_results['assignment_reverse'] = assignment_reverse
        dict_optimization_results['reverse_obj_val'] = reverse_obj_val
        dict_optimization_results['urgency_obj_val'] = urgency_obj_val
        return dict_optimization_results


    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
                Calculate the Haversine distance between two points on Earth.

                Args:
                    lat1 (float): Latitude of the first point.
                    lon1 (float): Longitude of the first point.
                    lat2 (float): Latitude of the second point.
                    lon2 (float): Longitude of the second point.

                Returns:
                    float: The distance between the two points in kilometers.
                """
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
        """
                Calculate the travel time between two points given a speed.

                Args:
                    lat1 (float): Latitude of the start point.
                    lon1 (float): Longitude of the start point.
                    lat2 (float): Latitude of the end point.
                    lon2 (float): Longitude of the end point.
                    speed (float): Travel speed in km/h.

                Returns:
                    float: The travel time in hours.
                """
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
        """
                Extract casualty information from mission options.

                Args:
                    missions_options (list): List of mission options.
                    persons (list): List to store person names.
                    person_score (dict): Dictionary to store person scores.
                    person_lsi_ts (dict): Dictionary to store LSI timestamps.
                    person_rtd_ts (dict): Dictionary to store RTD timestamps.
                    person_equipments_needed (dict): Dictionary to store equipment needs.
                    all_lats_longs (dict): Dictionary to store locations.

                Returns:
                    tuple: Updated lists and dictionaries with casualty information.
                """
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
        """
                Extract asset information.

                Args:
                    assets (list): List of assets.
                    assets_time_ranges (dict): Dictionary to store asset time ranges.
                    curr_asset_location (dict): Dictionary to store current asset locations.
                    assets_speeds (dict): Dictionary to store asset speeds.
                    all_lats_longs (dict): Dictionary to store locations.
                    assets_crew_duty_hrs (dict): Dictionary to store crew duty hours.

                Returns:
                    tuple: Updated lists and dictionaries with asset information.
                """
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
        """
                Extract care facility information.

                Args:
                    care_facilities (list): List of care facilities.
                    all_lats_longs (dict): Dictionary to store locations.

                Returns:
                    tuple: List of care facilities and updated locations dictionary.
                """
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
        """
                Calculate required timestamps for various combinations.

                Args:
                    persons (list): List of persons.
                    all_assets (list): List of all assets.
                    all_cfs (list): List of all care facilities.
                    all_lats_longs (dict): Dictionary of all locations.
                    curr_asset_location (dict): Dictionary of current asset locations.
                    assets_crew_duty_hrs (dict): Dictionary of asset crew duty hours.
                    assets_speeds (dict): Dictionary of asset speeds.
                    assets_time_ranges (dict): Dictionary of asset time ranges.

                Returns:
                    tuple: Dictionaries of required timestamps and distances.
                """
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
                    asset_p_dist = self.haversine_distance(asset_lat, asset_long, person_lat, person_long)
                    asset_p_time = asset_p_dist / assets_speeds[asset]
                    trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                            person_long) + self.haversine_distance(person_lat,
                                                                                                   person_long, cf_lat,
                                                                                                   cf_lon)
                    trip_time = trip_distance / assets_speeds[asset]
                    required_timesteps[(person, asset, cf)] = trip_time
                    required_distance[(person, asset, cf)] = trip_distance
                    required_timesteps_lsi_only[(person, asset, cf)] = asset_p_time

                    person_cf_d = self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                    person_cf_t = person_cf_d / assets_speeds[asset]

                    required_ts_asset_isop[(person, asset, cf)] = asset_p_time
                    required_ts_isop_cf[(person, asset, cf)] = person_cf_t

        return required_timesteps, required_distance, required_timesteps_lsi_only, required_ts_asset_isop, required_ts_isop_cf




    def return_triage_values(self, final_score):
        """
                Return triage values based on a final score.

                Args:
                    final_score (float): The final normalized triage score.

                Returns:
                    tuple: Triage category, LSI hours, RTD hours, and required resources based on normalized triage score.
        """
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

        return triage_category, lsi_hrs, rtd_hrs, resource_required
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)
    def create_pyreason_graph(self, missions_options: list[MissionOptionsAssets], assets: list[Asset], care_facilities: list[CareFacility], settings):
        """
                Create a PyReason graph from mission options, assets, and care facilities.

                Args:
                    missions_options (list[MissionOptionsAssets]): List of mission options.
                    assets (list[Asset]): List of assets.
                    care_facilities (list[CareFacility]): List of care facilities.
                    settings: Settings object containing configuration parameters.

                Returns:
                    nx.DiGraph: A directed graph for PyReason.
                """
        g = nx.DiGraph()

        for index, asset in enumerate(assets):
            record = asset.specifications_record
            asset_name = record['asset_name']
            asset_range_in_km = record['asset_range_in_km']
            asset_speed_kmph = record['asset_speed_kmph']
            asset_latitude = record['location'][0]
            asset_longitude = record['location'][1]
            g.add_node(asset_name, type_asset='1,1')
            g.add_node(asset_range_in_km, type_asset_range_in_km='1,1')
            g.add_node(asset_speed_kmph, type_asset_speed_kmph='1,1')
            g.add_node(asset_latitude, type_asset_latitude='1,1')
            g.add_node(asset_longitude, type_asset_longitude='1,1')
            g.add_edge(asset_name, asset_range_in_km, asset_range_in_km='1,1')
            g.add_edge(asset_name, asset_speed_kmph, asset_speed_kmph='1,1')
            g.add_edge(asset_name, asset_latitude, asset_latitude='1,1')
            g.add_edge(asset_name, asset_longitude, asset_longitude='1,1')

        for index, cf in enumerate(care_facilities):
            record = cf.specifications_record
            cf_name = record['cf_name']
            cf_latitude = record['location'][0]
            cf_longitude = record['location'][1]
            g.add_node(cf_name, type_cf='1,1')
            g.add_node(cf_latitude, type_cf_latitude='1,1')
            g.add_node(cf_longitude, type_cf_longitude='1,1')
            g.add_edge(cf_name, cf_latitude, cf_latitude='1,1')
            g.add_edge(cf_name, cf_longitude, cf_longitude='1,1')



        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            care_facilities_possible = mission.care_facilities_possible
            assets_possible = mission.assets_possible
            insults_dict = mission.insults_dict
            vitals_dict = mission.vitals_dict
            patient_latitude = mission.location[0]
            patient_longitude = mission.location[1]
            g.add_node(patient_name, type_casualty='1,1', insults_available='0,0', vitals_available='0,0')
            g.add_node(patient_latitude, type_cas_latitude='1,1')
            g.add_node(patient_longitude, type_cas_longitude='1,1')

            g.add_edge(patient_name, patient_latitude, cas_latitude='1,1')
            g.add_edge(patient_name, patient_longitude, cas_longitude='1,1')

            for possible_cf in care_facilities_possible:
                g.add_edge(patient_name, possible_cf, cf_possible='1,1')
            for possible_asset in assets_possible:
                g.add_edge(patient_name, possible_asset, asset_possible='1,1', assign_asset_urgency='0,0', assign_asset_reverse = '0,0')
            for insult, acs in insults_dict.items():
                insult = insult.replace('-', '_').replace(' ', '')
                if not g.has_node(insult):
                    g.add_node(insult, type_insult = '1,1')
                    nx.set_node_attributes(g, {insult: '1,1'}, f'type_{insult}')

                if pd.notnull(acs):
                    normalized_acs = round(acs*0.1, 2)
                    g.add_edge(patient_name, insult, normalized_acs=normalized_acs)
            for vital, value in vitals_dict.items():
                if not g.has_node(vital):
                    g.add_node(vital, type_vital = '1,1')
                    nx.set_node_attributes(g, {vital: '1,1'}, f'type_{vital}')

                if pd.notnull(value):
                    normalized_value = round(value*0.001, 4)
                    g.add_edge(patient_name, vital, value = normalized_value)
                    # nx.set_edge_attributes(g, {(patient_name, vital): normalized_value}, f'type_{vital}')

        enabled_triage_algos = settings.enabled_triage_algos
        enabled_urgency_opt = settings.enabled_urgency_opt
        enabled_reverse_opt = settings.enabled_reverse_opt
        constraints = settings.constraints

        for enabled_algo in enabled_triage_algos:
            if enabled_algo =='niss':
                g.add_node(enabled_algo, enable_niss = '1,1')
            elif enabled_algo =='rts':
                g.add_node(enabled_algo, enable_rts = '1,1')
            elif enabled_algo =='life':
                g.add_node(enabled_algo, enable_life = '1,1')

        if enabled_urgency_opt:
            g.add_node('urgency', use_opt='1,1', type_urgency = '1,1')
        else:
            g.add_node('urgency', use_opt='0,0', type_urgency = '1,1')

        if enabled_reverse_opt:
            g.add_node('reverse', use_opt='1,1', type_reverse = '1,1')
        else:
            g.add_node('reverse', use_opt='0,0', type_reverse = '1,1')
        g.add_node('None', type_none = '1,1')

        for constraint in constraints:
            g.add_node(constraint.constraint_name, use_constraint='1,1')
            nx.set_node_attributes(g, {constraint.constraint_name: '1,1'}, f'type_{constraint.constraint_name}')

            if constraint.constraint_name == 'air_time':
                g.add_edge('air_time', constraint.constraint_threshold, threshold='1,1')
        return g


    def initialize_pyreason(self, missions_options, assets, care_facilities, settings):
        """
                Initialize PyReason with the created graph and rules.

                Args:
                    missions_options: List of mission options.
                    assets: List of assets.
                    care_facilities: List of care facilities.
                    settings: Settings object containing configuration parameters.

                Returns:
                    dict: Dictionary of triage scores computed in pyreason.
                """
        pr.reset()
        pr.reset_rules()
        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True
        pr.settings.allow_ground_rules = True
        pr.add_annotation_function(rts_ann_fn)
        pr.add_annotation_function(niss_ann_fn)
        pr.add_annotation_function(life_ann_fn)
        pr.add_annotation_function(final_rts_ann_fn)
        pr.add_annotation_function(final_niss_ann_fn)

        graph = self.create_pyreason_graph(missions_options=missions_options, assets=assets, care_facilities=care_facilities, settings = settings)

        graphml_path = 'facts_graph.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_medevac_planning.txt'
        self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
        rules_path = os.path.join(current_script_directory, rules_path)
        pr.load_graphml(graphml_path)
        pr.add_rules_from_file(rules_path, infer_edges=True)
        # Reason at t=0
        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_0'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        dict_triage_scores = {}
        field = 'score'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    score = float(df[field][i][0])
                    if score == 0.00001:
                        score = 0.0
                    dict_triage_scores[df['component'][i]] = score
        return dict_triage_scores

    def get_filtered_casualties_info(self, dict_triage_scores, missions_options):
        """
                Filter and update casualty information based on triage scores.

                Args:
                    dict_triage_scores (dict): Dictionary of triage scores.
                    missions_options: List of mission options.

                Returns:
                    list: Filtered list of mission options.
                """
        for casualty, triage_score in dict_triage_scores.items():
            triage_category, lsi_ts, rtd_ts, equipments_needed = self.return_triage_values(final_score=triage_score)

            for index, mission in enumerate(missions_options):
                if mission.patient_name == casualty:
                    mission.triage_score = triage_score
                    mission.triage_category = triage_category
                    mission.lsi_ts = lsi_ts
                    mission.rtd_ts = rtd_ts
                    mission.equipments_needed = equipments_needed

        filtered_missions = [mission for mission in missions_options if
                             mission.patient_name in dict_triage_scores.keys()]
        return filtered_missions

    def get_final_assignments(self, dict_optimization_results):
        """
                Generate final assignments based on optimization results.

                Args:
                    dict_optimization_results (dict): Dictionary containing optimization results.

                Returns:
                    Plan: A Plan object containing urgency and reverse plans based on settings.
                """
        assignment_urgency = dict_optimization_results['assignment_urgency']
        assignment_reverse = dict_optimization_results['assignment_reverse']
        edge_facts = []
        node_facts = []
        if not pd.isna(assignment_urgency):
            for cas, (asset, cf, ts) in assignment_urgency.items():
                ts_minutes = int(ts * 60)
                pr.add_rule(
                    pr.Rule(rule_text=f'asset_free_urgency({asset}) <-{ts_minutes} assign_asset_urgency({cas},{asset})',
                            infer_edges=True))
                fact = pr.fact_edge.Fact(f'assignment_{cas}_urgency',
                                         (cas, asset),
                                         pr.label.Label('assign_asset_urgency'),
                                         pr.interval.closed(1, 1),
                                         self.next_time,
                                         self.next_time)
                fact_cf = pr.fact_edge.Fact(f'assignment_{cas}_urgency',
                                            (cas, cf),
                                            pr.label.Label('assign_cf_urgency'),
                                            pr.interval.closed(1, 1),
                                            self.next_time,
                                            self.next_time)
                edge_facts.append(fact)
                edge_facts.append(fact_cf)
        if not pd.isna(assignment_reverse):
            for cas, (asset, cf, ts) in assignment_reverse.items():
                ts_minutes = int(ts * 60)
                pr.add_rule(
                    pr.Rule(rule_text=f'asset_free_reverse({asset}) <-{ts_minutes} assign_asset_reverse({cas},{asset})',
                            infer_edges=True))
                fact = pr.fact_edge.Fact(f'assignment_{cas}_reverse',
                                         (cas, asset),
                                         pr.label.Label('assign_asset_reverse'),
                                         pr.interval.closed(1, 1),
                                         self.next_time,
                                         self.next_time)
                fact_cf = pr.fact_edge.Fact(f'assignment_{cas}_reverse',
                                            (cas, cf),
                                            pr.label.Label('assign_cf_reverse'),
                                            pr.interval.closed(1, 1),
                                            self.next_time,
                                            self.next_time)
                edge_facts.append(fact)
                edge_facts.append(fact_cf)

        # Reason at t=3
        self.interpretation = pr.reason(again=True, node_facts=node_facts, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t3_assignments'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        final_plans = Plan()
        final_plans.urgency_plan = assignment_urgency
        final_plans.reverse_plan = assignment_reverse

        return final_plans

    def generate_future_medevac_schedule(self, dict_optimization_instances, dict_optimization_results, schedule_type):

        schedule_dict = {}
        assets_schedule_start_timesteps = {}
        terminate = False
        run_urgency, run_reverse = False, False

        assignment_urgency = dict_optimization_results['assignment_urgency']
        assignment_reverse = dict_optimization_results['assignment_reverse']

        # before finding all saved casualties
        all_persons = dict_optimization_instances['persons']
        persons = all_persons.copy()
        person_scores = dict_optimization_instances['person_score']
        curr_asset_location = dict_optimization_instances['curr_asset_location']
        assets_time_ranges = dict_optimization_instances['assets_time_ranges']
        assets_crew_duty_hrs = dict_optimization_instances['assets_crew_duty_hrs']
        all_lats_longs = dict_optimization_instances['all_lats_longs']
        all_assets = dict_optimization_instances['all_assets']
        all_cfs = dict_optimization_instances['all_cfs']
        assets_speeds = dict_optimization_instances['assets_speeds']
        person_score = dict_optimization_instances['person_score']
        person_rtd_ts = dict_optimization_instances['person_rtd_ts']
        person_lsi_ts = dict_optimization_instances['person_lsi_ts']
        person_equipments_needed = dict_optimization_instances['person_equipments_needed']

        constraint_lsi = dict_optimization_instances['constraint_lsi']
        constraint_air_time = dict_optimization_instances['constraint_air_time']
        threshold_air = dict_optimization_instances['threshold_air']

        if schedule_type=='urgency':
            assignment_final = assignment_urgency.copy()
            run_urgency = True
        else:
            assignment_final = assignment_reverse.copy()
            run_reverse = True
        for asset in all_assets:
            assets_schedule_start_timesteps[asset] = 0

        for person, (asset, cf, ts) in assignment_final.items():
            if person not in persons:
                continue
            schedule_dict[(asset, curr_asset_location[asset], person, cf)] = (0, ts)
            assets_schedule_start_timesteps[asset] = ts + 1
            # assets_time_ranges[asset] -= ts
            # assets_crew_duty_hrs[asset] -= ts
            persons.remove(person)
            curr_asset_location[asset] = cf
        # Lets now iterate for rest of the schedule
        count_iterations = 0
        while (not terminate):
            required_timesteps = {}
            required_distance = {}
            required_timesteps_lsi_only = {}
            required_ts_asset_isop = {}
            required_ts_isop_cf = {}
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

                        asset_p_dist = self.haversine_distance(asset_lat, asset_long, person_lat, person_long)
                        asset_p_time = asset_p_dist / assets_speeds[asset]
                        trip_distance = self.haversine_distance(asset_lat, asset_long, person_lat,
                                                                person_long) + self.haversine_distance(person_lat,
                                                                                                       person_long,
                                                                                                       cf_lat,
                                                                                                       cf_lon)
                        trip_time = trip_distance / assets_speeds[asset]
                        required_timesteps[(person, asset, cf)] = trip_time + assets_schedule_start_timesteps[asset]
                        required_distance[(person, asset, cf)] = trip_distance
                        required_timesteps_lsi_only[(person, asset, cf)] = asset_p_time + assets_schedule_start_timesteps[asset]

                        person_cf_d = self.haversine_distance(person_lat, person_long, cf_lat, cf_lon)
                        person_cf_t = person_cf_d / assets_speeds[asset]

                        required_ts_asset_isop[(person, asset, cf)] = asset_p_time
                        required_ts_isop_cf[(person, asset, cf)] = person_cf_t

            if schedule_type=='reverse':
                assignment, reverse_obj_val, Z_reverse, Y_reverse = use_milp_reverse_triage(
                    persons=persons, assets=all_assets, hospitals=all_cfs, rtd_timesteps=person_rtd_ts,
                    required_timesteps=required_timesteps, required_timesteps_lsi_only=required_timesteps_lsi_only,
                    person_lsi_ts=person_lsi_ts, required_ts_asset_isop=required_ts_asset_isop,
                    required_ts_isop_cf=required_ts_isop_cf, constraint_lsi=constraint_lsi,
                    constraint_air_time=constraint_air_time,
                    threshold_air_time=threshold_air)
            elif schedule_type=='urgency':
                assignment, urgency_obj_val, Z_urgency, Y_urgency = use_milp_urgency_triage(persons=persons,
                                                                                                    assets=all_assets,
                                                                                                    hospitals=all_cfs,
                                                                                                    required_timesteps=required_timesteps,
                                                                                                    required_timesteps_lsi_only=required_timesteps_lsi_only,
                                                                                                    person_score=person_score,
                                                                                                    person_lsi_ts=person_lsi_ts,
                                                                                                    required_ts_asset_isop=required_ts_asset_isop,
                                                                                                    required_ts_isop_cf=required_ts_isop_cf,
                                                                                                    constraint_lsi=constraint_lsi,
                                                                                                    constraint_air_time=constraint_air_time,
                                                                                                    threshold_air_time=threshold_air)
            for person, (asset, cf, ts) in assignment.items():
                if person not in persons:
                    continue
                schedule_dict[(asset, curr_asset_location[asset], person, cf)] = (
                    assets_schedule_start_timesteps[asset], ts)
                assets_schedule_start_timesteps[asset] = ts + 1
                # assets_time_ranges[asset] -= ts
                curr_asset_location[asset] = cf
                persons.remove(person)
            count_iterations += 1
            if len(persons) == 0 or count_iterations > 10:
                terminate = True
        for (asset, curr_asset_loc, person, cf), (start_time, end_time) in schedule_dict.items():
            print((asset, curr_asset_loc, person, cf), '----> ', (start_time, end_time))
        return schedule_dict