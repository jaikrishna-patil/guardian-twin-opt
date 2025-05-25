from services.service_mission_options_care_facilities.AlgoMissionOptionsCFs import OptionsCFs

from services.models.ModelMissionOptionsCFs import MissionOptionsCFs
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelCareFacility import CareFacility

from datetime import datetime
import networkx as nx
import pyreason as pr
import os

class MissionOptionsCFsBasic(OptionsCFs):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'
    def create_pyreason_graph(self, mission_requirements: list[MissionRequirements], care_facilities: list[CareFacility]):
        g = nx.DiGraph()

        all_medical_services = ['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
        all_medical_specialities = ['trauma_surgery', 'emergency_medicine', 'orthopedic_surgery',
                                         'general_surgery'],
        all_medical_supplies = ['blood_bags', 'painkillers','antibiotics', 'anesthetics']


        # Model mission requirements
        for index,mission in enumerate(mission_requirements):
            record = mission.mission_requirements_record
            req_emergency_care = False
            req_surgical_services = False
            req_medical_imaging = False
            req_laboratory_services = False
            req_trauma_surgery = False
            req_emergency_medicine = False
            req_orthopedic_surgery = False
            req_general_surgery = False
            req_blood_bags = False
            req_painkillers = False
            req_antibiotics = False
            req_anesthetics = False
            for med_service in record['required_medical_services']:
                if med_service == 'emergency_care':
                    req_emergency_care = True
                elif med_service == 'surgical_services':
                    req_surgical_services = True
                elif med_service == 'medical_imaging':
                    req_medical_imaging = True
                elif med_service == 'laboratory_services':
                    req_laboratory_services = True
            for med_spec in record['required_medical_specialities']:
                if med_spec == 'trauma_surgery':
                    req_trauma_surgery = True
                elif med_spec == 'emergency_medicine':
                    req_emergency_medicine = True
                elif med_spec == 'orthopedic_surgery':
                    req_orthopedic_surgery = True
                elif med_spec == 'general_surgery':
                    req_general_surgery = True
            for med_supply in record['required_medical_supplies']:
                if med_supply == 'blood_bags':
                    req_blood_bags = True
                elif med_supply == 'painkillers':
                    req_painkillers = True
                elif med_supply == 'antibiotics':
                    req_antibiotics = True
                elif med_supply == 'anesthetics':
                    req_anesthetics = True
            g.add_node(record['name'],
                       type_mission = '1,1',
                       mission_id = index+2,
                       req_emergency_care = self.get_pyreason_bool(req_emergency_care),
                       req_surgical_services=self.get_pyreason_bool(req_surgical_services),
                       req_medical_imaging=self.get_pyreason_bool(req_medical_imaging),
                       req_laboratory_services=self.get_pyreason_bool(req_laboratory_services),
                       req_trauma_surgery = self.get_pyreason_bool(req_trauma_surgery),
                       req_emergency_medicine=self.get_pyreason_bool(req_emergency_medicine),
                       req_orthopedic_surgery = self.get_pyreason_bool(req_orthopedic_surgery),
                       req_general_surgery = self.get_pyreason_bool(req_general_surgery),
                       req_blood_bags=self.get_pyreason_bool(req_blood_bags),
                       req_painkillers=self.get_pyreason_bool(req_painkillers),
                       req_antibiotics=self.get_pyreason_bool(req_antibiotics),
                       req_anesthetics=self.get_pyreason_bool(req_anesthetics),
                       )
        for index, cf in enumerate(care_facilities):
            record = cf.specifications_record
            available_emergency_care = False
            available_surgical_services = False
            available_medical_imaging = False
            available_laboratory_services = False
            available_trauma_surgery = False
            available_emergency_medicine = False
            available_orthopedic_surgery = False
            available_general_surgery = False
            available_blood_bags = False
            available_painkillers = False
            available_antibiotics = False
            available_anesthetics = False
            for med_service in record['available_medical_services']:
                if med_service == 'emergency_care':
                    available_emergency_care = True
                elif med_service == 'surgical_services':
                    available_surgical_services = True
                elif med_service == 'medical_imaging':
                    available_medical_imaging = True
                elif med_service == 'laboratory_services':
                    available_laboratory_services = True
            for med_spec in record['available_medical_specialities']:
                if med_spec == 'trauma_surgery':
                    available_trauma_surgery = True
                elif med_spec == 'emergency_medicine':
                    available_emergency_medicine = True
                elif med_spec == 'orthopedic_surgery':
                    available_orthopedic_surgery = True
                elif med_spec == 'general_surgery':
                    available_general_surgery = True
            for med_supply in record['available_medical_supplies']:
                if med_supply == 'blood_bags':
                    available_blood_bags = True
                elif med_supply == 'painkillers':
                    available_painkillers = True
                elif med_supply == 'antibiotics':
                    available_antibiotics = True
                elif med_supply == 'anesthetics':
                    available_anesthetics = True
            g.add_node(record['cf_name'],
                       type_cf = '1,1',
                       cf_id = index+2,
                       available_emergency_care=self.get_pyreason_bool(available_emergency_care),
                       available_surgical_services=self.get_pyreason_bool(available_surgical_services),
                       available_medical_imaging=self.get_pyreason_bool(available_medical_imaging),
                       available_laboratory_services=self.get_pyreason_bool(available_laboratory_services),
                       available_trauma_surgery=self.get_pyreason_bool(available_trauma_surgery),
                       available_emergency_medicine=self.get_pyreason_bool(available_emergency_medicine),
                       available_orthopedic_surgery=self.get_pyreason_bool(available_orthopedic_surgery),
                       available_general_surgery=self.get_pyreason_bool(available_general_surgery),
                       available_blood_bags=self.get_pyreason_bool(available_blood_bags),
                       available_painkillers=self.get_pyreason_bool(available_painkillers),
                       available_antibiotics=self.get_pyreason_bool(available_antibiotics),
                       available_anesthetics=self.get_pyreason_bool(available_anesthetics),
                       )
            for mission in mission_requirements:
                record_mission = mission.mission_requirements_record
                mission_node = record_mission['name']
                for cf in care_facilities:
                    record_cf = cf.specifications_record
                    cf_node = record_cf['cf_name']
                    g.add_edge(mission_node, cf_node, option_cfs = '0,0',
                               emergency_care='0,0', surgical_services='0,0', medical_imaging='0,0', laboratory_services='0,0',
                               trauma_surgery='0,0', emergency_medicine='0,0', orthopedic_surgery='0,0', general_surgery='0,0',
                               blood_bags='0,0', painkillers='0,0', antibiotics='0,0', anesthetics='0,0'
                               )

        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_options_care_facilities(self, mission_requirements: list[MissionRequirements], care_facilities: list[CareFacility])\
            -> list[MissionOptionsCFs]:


        mission_options_care_facilities = []
        # Set pyreason settings
        graph = self.create_pyreason_graph(mission_requirements, care_facilities)
        graphml_path = 'pyreason_input_graph_mission_requirements_cfs.graphml'
        # Get the directory of the current script
        current_script_directory = os.path.dirname(os.path.abspath(__file__))
        # Define the path for the graphml file relative to the script's directory
        graphml_path = os.path.join(current_script_directory, graphml_path)

        rules_path = 'rules_mission_requirements_to_mission_options_care_facilities.txt'
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
        folder_name = 'traces_t0_mission_requirements_to_mission_options_cfs'
        folder_name = os.path.join(current_script_directory, folder_name)
        if not os.path.exists(folder_name):
            # Create the directory if it doesn't exist
            os.makedirs(folder_name)
        pr.save_rule_trace(self.interpretation, folder_name)
        dict_mission_cfs = {}
        field = 'option_cfs'
        df_outer = pr.filter_and_sort_edges(self.interpretation, [(field)])
        for t, df in enumerate(df_outer):
            if not df[field].empty:
                for i in range(len(df['component'])):
                    if df[field][i] == [1, 1]:
                        p_name = df['component'][i][0]
                        cf_name = df['component'][i][1]
                        if p_name not in dict_mission_cfs:
                            dict_mission_cfs[p_name] = [cf_name]
                        else:
                            dict_mission_cfs[p_name].append(cf_name)
        for key, value in dict_mission_cfs.items():
            mission_options_care_facilities.append(
                MissionOptionsCFs(
                    patient_name = key,
                    datetime_seconds=int(datetime.now().timestamp()),
                    algo_name='pyreason_basic',
                    care_facilities_possible=value,
                    care_facilities_details=None,
                    confidence=1.0,
                    rationale=None,
                    interaction=None
                )
            )

        return mission_options_care_facilities


