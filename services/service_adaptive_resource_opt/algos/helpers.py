import pyreason as pr
import networkx as nx
import os

from services.service_adaptive_resource_opt.algos.optimization_functions import solve_patient_resource_allocation_ip
from services.service_adaptive_resource_opt.algos.numba_annotation_functions import resupply_ann_fn
class Helper:

    def __init__(self):
        """
            Initialize the MedevacHelper instance.
        """
        self.interpretation = None
        self.next_time = 0

    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def normalize_mgap_score(self, mgap_score):
        max_score = 29
        min_score = 3
        normalized_score = (max_score - mgap_score) / (max_score - min_score)
        return normalized_score

    # def create_pyreason_graph_new(self, patients_dict, available_resources_dict):
    # def create_pyreason_graph(self, patients_dict, available_resources_dict):
    #
    #     g = nx.DiGraph()
    #     all_required_resources = []
    #
    #     for patient_name, patient_data in patients_dict.items():
    #         triage_mgap_score = patient_data['triage_score']
    #         normalized_mgap_score = self.normalize_mgap_score(mgap_score=triage_mgap_score)
    #         triage_category = patient_data['triage_category']
    #         required_resources = patient_data['required_resources']
    #         g.add_node(patient_name, type_patient='1,1', unserved_patient = '1,1')
    #         if not g.has_node(str(normalized_mgap_score)):
    #             g.add_node(str(normalized_mgap_score), type_score='1,1')
    #         g.add_edge(patient_name, str(normalized_mgap_score), triage_score='1,1')
    #
    #         if not g.has_node(triage_category):
    #             g.add_node(triage_category, type_triage_category='1,1')
    #         g.add_edge(patient_name, triage_category, triage_category='1,1')
    #
    #         for req_res, quantity in required_resources:
    #             if req_res not in all_required_resources:
    #                 all_required_resources.append(req_res)
    #             if not g.has_node(req_res):
    #                 g.add_node(req_res, type_resource='1,1')
    #             g.add_edge(patient_name, req_res, required_resource='1,1')
    #
    #
    #
    #
    #     for resource, quantity in available_resources_dict.items():
    #         all_required_resources.remove(resource)
    #         if not g.has_node(resource):
    #             g.add_node(resource, type_resource='1,1')
    #         if not g.has_node(str(quantity)):
    #             g.add_node(str(quantity))
    #         g.add_edge(resource, quantity, quantity_available='1,1')
    #
    #     for remianing_resource in all_required_resources:
    #         g.add_edge(remianing_resource, 0, quantity_available='1,1')
    #
    #     g.add_node('urgency', use_opt='1,1')
    #
    #
    #
    #
    #     return g
    #
    # def initialize_pyreason(self, patients_dict, available_resources_dict):
    #     pr.reset()
    #     pr.reset_rules()
    #     pr.settings.verbose = False
    #     pr.settings.atom_trace = True
    #     pr.settings.canonical = True
    #     pr.settings.inconsistency_check = False
    #     pr.settings.static_graph_facts = False
    #     pr.settings.save_graph_attributes_to_trace = True
    #     pr.settings.store_interpretation_changes = True
    #     pr.settings.allow_ground_rules = False
    #     pr.add_annotation_function(resupply_ann_fn)
    #
    #     graph = self.create_pyreason_graph(patients_dict, available_resources_dict)
    #
    #     graphml_path = 'facts_graph.graphml'
    #     # Get the directory of the current script
    #     current_script_directory = os.path.dirname(os.path.abspath(__file__))
    #     # Define the path for the graphml file relative to the script's directory
    #     graphml_path = os.path.join(current_script_directory, graphml_path)
    #
    #     rules_path = 'rules_deduction.txt'
    #     self.write_graphml(nx_graph=graph, graphml_path=graphml_path)
    #     rules_path = os.path.join(current_script_directory, rules_path)
    #     pr.load_graphml(graphml_path)
    #     pr.add_rules_from_file(rules_path, infer_edges=True)
    #     # Reason at t=0
    #     self.interpretation = pr.reason(0, again=False)
    #     self.next_time = self.interpretation.time + 1
    #     folder_name = 'traces_0'
    #     current_script_directory = os.path.dirname(os.path.abspath(__file__))
    #     folder_name = os.path.join(current_script_directory, folder_name)
    #     if not os.path.exists(folder_name):
    #         # Create the directory if it doesn't exist
    #         os.makedirs(folder_name)
    #     pr.save_rule_trace(self.interpretation, folder_name)
    #
    #     patients = []
    #     patients_scores = {}
    #     patient_requirements = {}
    #     resources = []
    #     resource_availability = {}
    #     final_criteria = None
    #     field = 'unserved_patient'
    #     df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
    #     for t, df in enumerate(df_outer):
    #         for index, row in df.iterrows():
    #             patient_name = row['component']
    #             unserved_flag = row[field]
    #             if unserved_flag == [1,1]:
    #                 patients.append(patient_name)
    #
    #     for patient in patients:
    #         patient_requirements[patient] = {}
    #
    #     field = 'triage_score'
    #     df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
    #     for t, df in enumerate(df_outer):
    #         for index, row in df.iterrows():
    #             patient_name, score = row['component']
    #             score_flag = row[field]
    #             if score_flag == [1,1]:
    #                 patients_scores[patient_name] = round(float(score), 3)
    #
    #     field = 'required_resource'
    #     df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
    #     for t, df in enumerate(df_outer):
    #         for index, row in df.iterrows():
    #             patient_name, req_resource = row['component']
    #             req_resource_flag = row[field]
    #             if req_resource_flag == [1, 1]:
    #                 if req_resource not in patient_requirements[patient_name].keys():
    #                     patient_requirements[patient_name][req_resource] = 1
    #                 else:
    #                     patient_requirements[patient_name][req_resource] += 1
    #
    #     field = 'type_resource'
    #     df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
    #     for t, df in enumerate(df_outer):
    #         for index, row in df.iterrows():
    #             resource = row['component']
    #             resource_flag = row[field]
    #             if resource_flag == [1, 1]:
    #                 resources.append(resource)
    #
    #     field = 'quantity_available'
    #     df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
    #     for t, df in enumerate(df_outer):
    #         for index, row in df.iterrows():
    #             resource, quantity = row['component']
    #             available_resource_flag = row[field]
    #             if available_resource_flag == [1, 1]:
    #                 resource_availability[resource] = int(quantity)
    #
    #     field = 'run_opt'
    #     df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
    #     for t, df in enumerate(df_outer):
    #         for index, row in df.iterrows():
    #             opt_criteria = row['component']
    #             opt_flag = row[field]
    #             if opt_flag == [1, 1]:
    #                 final_criteria = opt_criteria
    #     return patients, patients_scores, patient_requirements, resources, resource_availability, final_criteria
    def create_pyreason_graph(self, patients_dict, injuries_dict, interventions_dict, available_resources_dict):

        g = nx.DiGraph()
        all_required_resources = set()

        for patient_name, patient_data in patients_dict.items():
            triage_mgap_score = patient_data['triage_score']
            normalized_mgap_score = self.normalize_mgap_score(mgap_score=triage_mgap_score)
            triage_category = patient_data['triage_category']
            has_injuries = patient_data['has_injuries']
            g.add_node(patient_name, type_patient='1,1', unserved_patient = '1,1')
            if not g.has_node(str(normalized_mgap_score)):
                g.add_node(str(normalized_mgap_score), type_score='1,1')
            g.add_edge(patient_name, str(normalized_mgap_score), triage_score='1,1')

            if not g.has_node(triage_category):
                g.add_node(triage_category, type_triage_category='1,1')
            g.add_edge(patient_name, triage_category, triage_category='1,1')

            for injury_id in has_injuries:
                if not g.has_node(str(injury_id)):
                    g.add_node(str(injury_id), type_injury='1,1')
                g.add_edge(patient_name, str(injury_id), has_injury='1,1')

        for injury_id, injury_data in injuries_dict.items():
            injury_label = injury_data['injury_label']
            need_interventions = injury_data['need_interventions']

            if not g.has_node(str(injury_id)):
                g.add_node(str(injury_id), type_injury='1,1')
            if not g.has_node(injury_label):
                g.add_node(injury_label, type_injury_name='1,1')
            g.add_edge(str(injury_id), injury_label, injury_label='1,1')

            for intervention_id in need_interventions:
                if not g.has_node(str(intervention_id)):
                    g.add_node(str(intervention_id), type_intervention='1,1')
                g.add_edge(str(injury_id), str(intervention_id), need_intervention='1,1')

        for intervention_id, intervention_data in interventions_dict.items():
            intervention_label = intervention_data['intervention_label']
            includes_resources = intervention_data['includes_resources']

            if not g.has_node(str(intervention_id)):
                g.add_node(str(intervention_id), type_intervention='1,1')
            if not g.has_node(str(intervention_label)):
                g.add_node(str(intervention_label), type_intervention_label='1,1')
            g.add_edge(str(intervention_id), str(intervention_label), intervention_label='1,1')

            for resource_name in includes_resources:
                all_required_resources.add(resource_name)
                if not g.has_node(str(resource_name)):
                    g.add_node(str(resource_name), type_resource='1,1')
                g.add_edge(intervention_id, str(resource_name), includes_resource='1,1')




        for resource, quantity in available_resources_dict.items():
            all_required_resources.discard(resource)
            if not g.has_node(resource):
                g.add_node(resource, type_resource='1,1')
            if not g.has_node(str(quantity)):
                g.add_node(str(quantity))
            g.add_edge(resource, quantity, quantity_available='1,1')

        for remianing_resource in all_required_resources:
            g.add_edge(remianing_resource, 0, quantity_available='1,1')

        g.add_node('urgency', use_opt='1,1')




        return g

    def initialize_pyreason(self, patients_dict, injuries_dict, interventions_dict, available_resources_dict):
        pr.reset()
        pr.reset_rules()
        pr.settings.verbose = False
        pr.settings.atom_trace = True
        pr.settings.canonical = True
        pr.settings.inconsistency_check = False
        pr.settings.static_graph_facts = False
        pr.settings.save_graph_attributes_to_trace = True
        pr.settings.store_interpretation_changes = True
        pr.settings.allow_ground_rules = False
        pr.add_annotation_function(resupply_ann_fn)

        graph = self.create_pyreason_graph(patients_dict, injuries_dict, interventions_dict, available_resources_dict)

        graphml_path = 'facts_graph.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_deduction.txt'
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

        patients = []
        patients_scores = {}
        patient_requirements = {}
        resources = []
        resource_availability = {}
        final_criteria = None
        field = 'unserved_patient'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            for index, row in df.iterrows():
                patient_name = row['component']
                unserved_flag = row[field]
                if unserved_flag == [1,1]:
                    patients.append(patient_name)

        for patient in patients:
            patient_requirements[patient] = {}

        field = 'triage_score'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            for index, row in df.iterrows():
                patient_name, score = row['component']
                score_flag = row[field]
                if score_flag == [1,1]:
                    patients_scores[patient_name] = round(float(score), 3)

        field = 'required_resource'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            for index, row in df.iterrows():
                patient_name, req_resource = row['component']
                req_resource_flag = row[field]
                if req_resource_flag == [1, 1]:
                    if req_resource not in patient_requirements[patient_name].keys():
                        patient_requirements[patient_name][req_resource] = 1
                    else:
                        patient_requirements[patient_name][req_resource] += 1

        field = 'type_resource'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            for index, row in df.iterrows():
                resource = row['component']
                resource_flag = row[field]
                if resource_flag == [1, 1]:
                    resources.append(resource)

        field = 'quantity_available'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            for index, row in df.iterrows():
                resource, quantity = row['component']
                available_resource_flag = row[field]
                if available_resource_flag == [1, 1]:
                    resource_availability[resource] = int(quantity)

        field = 'run_opt'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            for index, row in df.iterrows():
                opt_criteria = row['component']
                opt_flag = row[field]
                if opt_flag == [1, 1]:
                    final_criteria = opt_criteria
        return patients, patients_scores, patient_requirements, resources, resource_availability, final_criteria

    def run_opt(self, patients, patients_scores, patient_requirements, resources, resource_availability, final_criteria):

        served_patients = []
        if final_criteria == 'urgency':
            served_patients = solve_patient_resource_allocation_ip(patients=patients, patients_scores=patients_scores, patient_requirements=patient_requirements, resources=resources, resource_availability=resource_availability)

        return served_patients

    def update_pyreason_facts(self, patients, patients_scores, patient_requirements, resources, resource_availability, served_patients):

        node_facts = []
        edge_facts = []

        for patient in served_patients:
            fact = pr.fact_node.Fact(f'fact_unserved_{patient}',
                                     patient,
                                     pr.label.Label('unserved_patient'),
                                     pr.interval.closed(0,0),
                                     self.next_time,
                                     self.next_time)
            node_facts.append(fact)

            for req_resource, qt in patient_requirements[patient].items():
                fact = pr.fact_edge.Fact(f'fact_req_{patient}',
                                     (patient, req_resource),
                                     pr.label.Label('required_resource'),
                                     pr.interval.closed(0,0),
                                     self.next_time,
                                     self.next_time)
                edge_facts.append(fact)


                fact = pr.fact_edge.Fact(f'fact_avail_{req_resource}',
                                     (req_resource, str(resource_availability[req_resource])),
                                     pr.label.Label('quantity_available'),
                                     pr.interval.closed(0,0),
                                     self.next_time,
                                     self.next_time)
                edge_facts.append(fact)

                new_available_resource_qty = resource_availability[req_resource] - 1
                resource_availability[req_resource] = new_available_resource_qty

                fact = pr.fact_edge.Fact(f'fact_avail_{req_resource}',
                                         (req_resource, str(resource_availability[req_resource])),
                                         pr.label.Label('quantity_available'),
                                         pr.interval.closed(1, 1),
                                         self.next_time,
                                         self.next_time)
                edge_facts.append(fact)



            for resource in resources:
                if resource in patient_requirements[patient].items():
                    patient_requirements[patient][resource] = 0

        unserved_patients = list(set(patients) - set(served_patients))
        dict_required_resources_qty_total = {}
        for patient in unserved_patients:
            for req_resource, qt in patient_requirements[patient].items():
                if req_resource not in dict_required_resources_qty_total:
                    dict_required_resources_qty_total[req_resource] = qt
                else:
                    dict_required_resources_qty_total[req_resource] += qt

        # for req_resource, needed_qt in dict_required_resources_qty_total.items():
        #     fact = pr.fact_edge.Fact(f'fact_needed_{req_resource}',
        #                              (req_resource, str(needed_qt)),
        #                              pr.label.Label('total_quantity_needed'),
        #                              pr.interval.closed(1, 1),
        #                              self.next_time,
        #                              self.next_time)
        #     edge_facts.append(fact)
        for req_resource, needed_qt in dict_required_resources_qty_total.items():
            if needed_qt >0:
                pr_qt = round(needed_qt*0.001, 6)
                fact = pr.fact_node.Fact(f'fact_needed_{req_resource}',
                                         req_resource,
                                         pr.label.Label('total_quantity_needed'),
                                         pr.interval.closed(pr_qt, 1),
                                         self.next_time,
                                         self.next_time)
                node_facts.append(fact)
            elif needed_qt == 0:
                fact = pr.fact_node.Fact(f'fact_needed_{req_resource}',
                                         req_resource,
                                         pr.label.Label('total_quantity_needed'),
                                         pr.interval.closed(0,0),
                                         self.next_time,
                                         self.next_time)
                node_facts.append(fact)
        for res, available_qty in resource_availability.items():
            if available_qty > 0:
                pr_qt = round(available_qty * 0.001, 6)
                fact = pr.fact_node.Fact(f'fact_avail_{res}',
                                         res,
                                         pr.label.Label('total_quantity_available'),
                                         pr.interval.closed(pr_qt, 1),
                                         self.next_time,
                                         self.next_time)
                node_facts.append(fact)
            elif available_qty == 0:
                fact = pr.fact_node.Fact(f'fact_avail_{res}',
                                         res,
                                         pr.label.Label('total_quantity_available'),
                                         pr.interval.closed(0, 0),
                                         self.next_time,
                                         self.next_time)
                node_facts.append(fact)

        # Reason at t=1

        self.interpretation = pr.reason(again=True, node_facts=node_facts, edge_facts=edge_facts)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_1'
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)














