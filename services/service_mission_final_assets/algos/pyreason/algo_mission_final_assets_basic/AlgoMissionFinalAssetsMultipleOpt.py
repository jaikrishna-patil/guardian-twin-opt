from services.service_mission_final_assets.AlgoMissionFinalAssets import FinalAssets

from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelMissionFinalAssets import MissionFinalAssets
from services.models.ModelConstraints import Constraint

from datetime import datetime
import networkx as nx
import pyreason as pr
import os

from mip import Model, xsum, maximize, BINARY, OptimizationStatus

class MissionFinalAssetsMultipleOpt(FinalAssets):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0



    def use_milp(self, dict_triage_score: dict, dict_possible_assets: dict, constraint_1: bool,
                 constraint_2: bool) -> dict:
        persons = list(dict_triage_score.keys())
        w_p = {}
        resources_persons = []
        unique_assets = set()

        # Calculate weights and collect possible resources for each person
        for person, score in dict_triage_score.items():
            w_p[person] = 1 - score
        for person, possible_assets in dict_possible_assets.items():
            unique_assets.update(possible_assets)
            for asset in possible_assets:
                resources_persons.append((asset, person))
        resources = list(unique_assets)

        # Convert names to indices
        person_index = {person: i for i, person in enumerate(persons)}
        resource_index = {resource: i for i, resource in enumerate(resources)}

        low_triage_persons = [person for person, score in dict_triage_score.items() if score < 50]

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

        # Create binary variables for each resource to track if it is used
        R = [m.add_var(var_type=BINARY) for _ in resources]

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

        # Add constraint: limit the number of used resources to a maximum of 3
        if constraint_1:
            m += xsum(R[r_idx] for r_idx in range(len(resources))) <= 3

            # Add constraint: link X and R variables
            for (r_idx, p_idx) in X.keys():
                m += X[(r_idx, p_idx)] <= R[r_idx]

        # Add constraint: all persons with triage scores less than 50 must be assigned at least one resource
        if constraint_2:
            for person in low_triage_persons:
                p_idx = person_index[person]
                m += Y[p_idx] == 1

        # Optimize the model
        status = m.optimize()

        # Extract and print the selected persons and their assigned resources
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            selected_persons = [p for p in persons if Y[person_index[p]].x is not None and Y[person_index[p]].x >= 0.99]
            assigned_resources = [(resources[r_idx], persons[p_idx]) for (r_idx, p_idx) in X.keys() if
                                  X[(r_idx, p_idx)].x is not None and X[(r_idx, p_idx)].x >= 0.99]
        else:
            selected_persons = []
            assigned_resources = []

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

            g.add_edge('instance_both', patient_name, pre_assign_instance_person='0,0')
            g.add_edge('instance_1', patient_name, pre_assign_instance_person='0,0')
            g.add_edge('instance_0', patient_name, pre_assign_instance_person='0,0')

            for i in range(len(possible_assets)):
                g.add_edge(patient_name, possible_assets[i], possible_asset='1,1', final_asset='0,0')
                g.add_edge('instance_both', possible_assets[i], pre_assign_instance_asset='0,0')
                g.add_edge('instance_1', possible_assets[i], pre_assign_instance_asset='0,0')
                g.add_edge('instance_0', possible_assets[i], pre_assign_instance_asset='0,0')



        g.add_node('instance_both', pred_instance_both='1,1', is_empty='1,1', use_instance_both='0,1', use_instance_1='0,1', use_instance_0='0,1')
        g.add_node('instance_1', pred_instance_1='1,1', is_empty='1, 1', use_instance_both='0,1', use_instance_1='0,1', use_instance_0='0,1')
        g.add_node('instance_2', pred_instance_2='1,1', is_empty='1, 1', use_instance_both='0,1', use_instance_1='0,1', use_instance_0='0,1')
        g.add_node('instance_0', pred_instance_0='1,1', is_empty='1, 1', use_instance_both='0,1', use_instance_1='0,1', use_instance_0='0,1')



        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_final_asset_opt(self, missions_options: list[MissionOptionsAssets], constraints = list[Constraint]) -> list[MissionFinalAssets]:


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

        print(dict_patients_triage_score)
        _, assigned_persons_resource_constraint_both = self.use_milp(dict_triage_score=dict_patients_triage_score, dict_possible_assets=dict_patients_possible_assets, constraint_1=True, constraint_2=True)
        _, assigned_persons_resource_constraint_1 = self.use_milp(dict_triage_score=dict_patients_triage_score, dict_possible_assets=dict_patients_possible_assets, constraint_1=True, constraint_2=False)
        _, assigned_persons_resource_constraint_0 = self.use_milp(dict_triage_score=dict_patients_triage_score, dict_possible_assets=dict_patients_possible_assets, constraint_1=False, constraint_2=False)

        print(assigned_persons_resource_constraint_both)
        print(assigned_persons_resource_constraint_1)
        print(assigned_persons_resource_constraint_0)

        edge_facts = []
        node_facts = []

        for a_name, p_name in assigned_persons_resource_constraint_both:
            fact_constr_both = pr.fact_edge.Fact(f'f_mlp_result_both', (p_name, a_name),
                                               pr.label.Label('pre_assign_constraint_both'),
                                               pr.interval.closed(1, 1),
                                               self.next_time,
                                               self.next_time)
            edge_facts.append(fact_constr_both)

        for a_name, p_name in assigned_persons_resource_constraint_1:
            fact_constr1 = pr.fact_edge.Fact(f'f_mlp_result_c1', (p_name, a_name),
                                               pr.label.Label('pre_assign_constraint_1'),
                                               pr.interval.closed(1, 1),
                                               self.next_time,
                                               self.next_time)
            edge_facts.append(fact_constr1)

        for a_name, p_name in assigned_persons_resource_constraint_0:
            fact_constr0 = pr.fact_edge.Fact(f'f_mlp_result_c0', (p_name, a_name),
                                               pr.label.Label('pre_assign_constraint_0'),
                                               pr.interval.closed(1, 1),
                                               self.next_time,
                                               self.next_time)
            edge_facts.append(fact_constr0)


        # Reason at t=1
        self.interpretation = pr.reason(again=True, node_facts=node_facts, edge_facts=edge_facts)
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


