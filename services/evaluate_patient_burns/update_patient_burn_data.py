import os
import sys
import yaml
from gt_service_tools.services.evaluate_patient_burns.evaluate_patient_burns import EvaluatePatientBurns


class UpdatePatientBurnData:
    def __init__(self):
        self.evaluate_patient_burns = EvaluatePatientBurns()
        self.scenario_path = None
        self.patients_states = None
        
    def get_scenario_path(self, scenario):
        scenario_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'scenario_data'))
        self.scenario_path = os.path.join(scenario_data_path, scenario)
        return self.scenario_path
        
    def get_patients_states(self):
        patients_state_file = os.path.join(self.scenario_data_path, 'isop_states.yaml' or 'patients_states.yaml')
        with open(patients_state_file, 'r') as f:
            patients_states = yaml.safe_load(f)
        return patients_states
    
    def get_patients_details(self):
        patients_details_file = os.path.join(self.scenario_data_path, 'isop_details.yaml' or 'patients_details.yaml')
        with open(patients_details_file, 'r') as f:
            patients_details = yaml.safe_load(f)
        return patients_details
        
        
    # Iterate through the patients in self.patients_states and evaluate their burn injuries. then update the patient data in the isop_states.yaml file with the burn injury groups
    def update_patients_burn_data(self, tbsa_algo=None):
        for patient in self.patients_states:
            patient_insults = patient.get('patient_record').get('insults', [])
            patient_id = patient.get('patient_id') or patient.get('isop_id')
            # To get the patient age, we need to use the patient_id to find the matching patient details in the self.patients_details and then get the age from the patient details
            patient_details = [patient for patient in self.patients_details if patient.get('patient_id') or patient.get('isop_id') == patient_id]
            if not patient_details:
                raise ValueError(f"Patient details not found for patient_id: {patient_id}")
            patient_age = patient_details.get('age')
            self.evaluate_patient_burns.evaluate_burn_injuries(patient_insults, tbsa_algo, patient_age)
            self.evaluate_patient_burns.create_burn_injury_groups()
            patient['burn_injury_groups'] = self.evaluate_patient_burns.burn_injury_groups
        return self.patients_states