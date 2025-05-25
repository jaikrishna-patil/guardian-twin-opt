from services.service_mission_final_assets.AlgoMissionFinalAssets import FinalAssets

from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets

from datetime import datetime
import networkx as nx
import pyreason as pr
import os

from mip import Model, xsum, maximize, BINARY

class MissionFinalAssetsBasic(FinalAssets):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0
    def use_milp(self, dict_triage_score:dict, dict_possible_assets:dict) -> dict:
        persons = list(dict_triage_score.keys())
        w_p = {}
        resources_persons = []
        unique_assets = set()
        for person, score in dict_triage_score.items():
            w_p[person] = 1-score
        for person, possible_assets in dict_possible_assets.items():
            unique_assets.update(possible_assets)
            for asset in possible_assets:
                resources_persons.append((asset, person))
        resources = list(unique_assets)

        # Convert names to indices
        person_index = {person: i for i, person in enumerate(persons)}
        resource_index = {resource: i for i, resource in enumerate(resources)}

        # Create a new model
        m = Model("resource_person_assignment")

        # Create binary variables for each valid resource-person pair
        X = {}
        for r, p in resources_persons:
            r_idx = resource_index[r]
            p_idx = person_index[p]
            X[(r_idx, p_idx)] = m.add_var(var_type=BINARY)

        # Create binary variables for each person
        Y = [m.add_var(var_type=BINARY) for _ in persons]

        # Set the objective to maximize the total weight (value) of selected persons
        m.objective = maximize(xsum(Y[person_index[p]] * w_p[p] for p in persons))

        # Add constraints: sum of X[r, p] for all resources r must be at least Y[p] for each person p
        for p in persons:
            p_idx = person_index[p]
            m += xsum(X[(r_idx, p_idx)] for r_idx, p_idx2 in X.keys() if p_idx2 == p_idx) >= Y[p_idx]

        # Add constraints: each resource can be assigned to at most one person
        for r in resources:
            r_idx = resource_index[r]
            m += xsum(X[(r_idx, p_idx)] for r_idx2, p_idx in X.keys() if r_idx2 == r_idx) <= 1

        # Optimize the model
        m.optimize()

        # Extract and print the selected persons and their assigned resources
        selected_persons = [p for p in persons if Y[person_index[p]].x >= 0.99]
        assigned_resources = [(resources[r_idx], persons[p_idx]) for (r_idx, p_idx) in X.keys() if
                              X[(r_idx, p_idx)].x >= 0.99]

        # print("Selected persons:", selected_persons)
        # print("Assigned resources:", assigned_resources)
        return selected_persons, assigned_resources


    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'
    def create_pyreason_graph(self, missions_options: list[MissionOptionsAssets]):
        g = nx.DiGraph()
        unique_assets = set()
        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            triage_score = mission.triage_score
            possible_assets = mission.assets_possible
            g.add_node(patient_name, type_patient = '1,1')
            g.add_edge(patient_name, str(triage_score), triage_score='1,1')

            unique_assets.update(possible_assets)

        for asset in unique_assets:
            g.add_node(asset, type_asset = '1,1')
        for index, mission in enumerate(missions_options):
            patient_name = mission.patient_name
            possible_assets = mission.assets_possible

            for i in range(len(possible_assets)):
                g.add_edge(patient_name, possible_assets[i], possible_asset='1,1', final_asset='0,1')



        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_final_asset(self, missions_options: list[MissionOptionsAssets]) -> list[MissionFinalAssets]:


        mission_final_assets = []
        # Set pyreason settings
        graph = self.create_pyreason_graph(missions_options)
        graphml_path = 'pyreason_input_graph_mission_options_assets.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_mission_options_assets_to_final_assets.txt'
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
        folder_name = 'traces_t0_mission_options_assets_to_final_assets'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        patients_list = []
        field = 'trigger_optimization'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        p_name = df['component'][i]
                        patients_list.append(p_name)

        dict_patients_triage_score = {}
        field = 'triage_score'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        p_name = df['component'][i][0]
                        triage_score = float(df['component'][i][1])
                        triage_score = triage_score/100
                        if p_name in patients_list:
                            dict_patients_triage_score[p_name]= triage_score

        dict_patients_possible_assets = {}
        for p in patients_list:
            dict_patients_possible_assets[p] = []

        field = 'possible_asset'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        p_name = df['component'][i][0]
                        a_name = df['component'][i][1]
                        if p_name in patients_list:
                           dict_patients_possible_assets[p_name].append(a_name)
        _, assigned_persons_resource = self.use_milp(dict_triage_score=dict_patients_triage_score, dict_possible_assets=dict_patients_possible_assets)

        edge_facts = []
        node_facts = []

        for index, assigned_person_resource in enumerate(assigned_persons_resource):
            fact_mlp_result = pr.fact_edge.Fact(f'f_mlp_result_{index}', (assigned_person_resource[1], assigned_person_resource[0]),
                                               pr.label.Label('mlp_optimized'),
                                               pr.interval.closed(1, 1),
                                               self.next_time,
                                               self.next_time)
            edge_facts.append(fact_mlp_result)

        # Reason at t=1
        self.interpretation = pr.reason(again=True, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t1_mission_options_assets_to_final_assets'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)

        dict_patients_final_asset = {}

        field = 'final_asset'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        p_name = df['component'][i][0]
                        a_name = df['component'][i][1]
                        dict_patients_final_asset[p_name]= a_name
        for patient in patients_list:
            if patient not in dict_patients_final_asset:
                dict_patients_final_asset[patient] = 'NA'
        for key, value in dict_patients_final_asset.items():
            mission_final_assets.append(
                MissionFinalAssets(
                    patient_name = key,
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name='pyreason_basic',
                    asset_final=value,
                    asset_details=None,
                    confidence=1.0,
                    rationale=None,
                    interaction=None
                )
            )

        return mission_final_assets


