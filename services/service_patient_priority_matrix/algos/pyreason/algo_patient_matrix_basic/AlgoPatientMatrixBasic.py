from services.service_patient_priority_matrix.AlgoPatientPriorityMatrix import PatientPriority

from services.models.ModelPatientMatrix import RationaleRecord, PatientMatrix
from services.models.ModelPatient import Patient

from datetime import datetime
import networkx as nx
import pyreason as pr
import os

class PatientMatrixBasic(PatientPriority):

    def __init__(self):
        # self.thresholds = thresholds
        self.interpretation = None
        self.next_time = 0

    def create_pyreason_graph(self, patients_cat: list[Patient]):
        g = nx.DiGraph()



        # Add triage categories
        g.add_node('expectant', triage_category_id = 2, type_triage_category_expectant='1,1')
        g.add_node('immediate', triage_category_id=3, type_triage_category_immediate='1,1')
        g.add_node('urgent', triage_category_id=4, type_triage_category_urgent='1,1')
        g.add_node('delayed', triage_category_id=5, type_triage_category_delayed='1,1')
        g.add_node('minor', triage_category_id=6, type_triage_category_minor='1,1')
        g.add_node('uninjured', triage_category_id=7, type_triage_category_uninjured='1,1')

        # Add priorities 0 to 6
        g.add_node(str(0), priority_zero='1,1')
        g.add_node(str(1), priority_one='1,1')
        g.add_node(str(2), priority_two='1,1')
        g.add_node(str(3), priority_three='1,1')
        g.add_node(str(4), priority_four='1,1')
        g.add_node(str(5), priority_five='1,1')
        g.add_node(str(6), priority_six='1,1')

        # Add casualties
        for index, patient in enumerate(patients_cat):
            record = patient.physiology_record
            patient_name = record['name']
            patient_category = record['category']
            g.add_node(patient_name, casualty_id=index+2, type_casualty='1,1', litter='0,0', ambulatory='1,1',
                       medevac_needed='0,0', evac_needed='0,0', resupply_needed='0,0')

            # Edge casualty,category
            g.add_edge(patient_name, patient_category, triage_category='1,1')

            # Target edge :: casualty, priority
            for i in range(0,7):
                g.add_edge(patient_name, str(i), medevac_priority='0,0', evac_priority='0,0', resupply_priority='0,0')

        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)
    def return_patient_priority_matrix(self, patients_categories: list[Patient]) -> list[PatientMatrix]:


        patients_priority_matrices =[]
        # Set pyreason settings

        graph = self.create_pyreason_graph(patients_categories)
        graphml_path = 'pyreason_input_graph_triage_categories.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_triage_category_to_patient_priority_matrix.txt'
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
        pr.add_rules_from_file(rules_path)

        # Reason at t=0
        self.interpretation = pr.reason(0, again=False)
        self.next_time = self.interpretation.time + 1
        folder_name = 'traces_t0_triage_category_to_patient_priority_matrix'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)


        patient_detail = {}
        field = 'litter'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1,1]:
                        patient_detail[df['component'][i]] = {field: True}
                    else:
                        patient_detail[df['component'][i]] = {field: False}

        field = 'ambulatory'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i]][field] = True
                    else:
                        patient_detail[df['component'][i]][field] = False
        field = 'medevac_needed'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i]][field] = True
                    else:
                        patient_detail[df['component'][i]][field] = False
        field = 'evac_needed'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i]][field] = True
                    else:
                        patient_detail[df['component'][i]][field] = False
        field = 'resupply_needed'
        df_outer = pr.filter_and_sort_nodes(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i]][field] = True
                    else:
                        patient_detail[df['component'][i]][field] = False

        field = 'medevac_priority'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i][0]][field] = df['component'][i][1]
        field = 'evac_priority'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i][0]][field] = df['component'][i][1]
        field = 'resupply_priority'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        patient_detail[df['component'][i][0]][field] = df['component'][i][1]
        for p_name, p_details in patient_detail.items():
            patients_priority_matrices.append(
                PatientMatrix(
                    patient_name = p_name,
                    datetime_seconds = int(datetime.now().timestamp()),
                    algo_name = 'pyreason_basic',
                    litter = p_details['litter'],
                    ambulatory = p_details['ambulatory'],
                    medevac_needed = p_details['medevac_needed'],
                    medevac_priority = p_details['medevac_priority'],
                    evac_needed = p_details['evac_needed'],
                    evac_priority = p_details['evac_priority'],
                    resupply_needed = p_details['resupply_needed'],
                    resupply_priority = p_details['resupply_priority'],
                    confidence = 1.0,
                    rationale = None,
                    interaction = None
                )
            )
        return patients_priority_matrices

