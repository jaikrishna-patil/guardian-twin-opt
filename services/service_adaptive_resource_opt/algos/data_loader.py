import os
import yaml


class DataLoader:

    def load_data(self, data_dir):
        # Load all YAML files
        injuries_data = self.load_injuries(os.path.join(data_dir, 'injuries.yaml'))
        interventions_data = self.load_interventions(os.path.join(data_dir, 'interventions.yaml'))
        merts_data = self.load_merts(os.path.join(data_dir, 'merts.yaml'))
        patients_data = self.load_patients(os.path.join(data_dir, 'patients.yaml'))

        # Create patients_dict and available_resources_dict
        patients_dict = self.create_patients_dict(patients_data, injuries_data)
        available_resources_dict = self.create_available_resources_dict(merts_data)

        return patients_dict, available_resources_dict

    def load_data_new(self, data_dir):
        # Load all YAML files
        injuries_data = self.load_injuries(os.path.join(data_dir, 'injuries.yaml'))
        interventions_data = self.load_interventions(os.path.join(data_dir, 'interventions.yaml'))
        merts_data = self.load_merts(os.path.join(data_dir, 'merts.yaml'))
        patients_data = self.load_patients(os.path.join(data_dir, 'patients.yaml'))

        # Create patients_dict and available_resources_dict
        patients_dict = self.create_patients_dict_new(patients_data)
        injuries_dict = self.create_injuries_dict(injuries_data)
        interventions_dict = self.create_interventions_dict(interventions_data)
        available_resources_dict = self.create_available_resources_dict(merts_data)

        return patients_dict, injuries_dict, interventions_dict, available_resources_dict

    def load_injuries(self, file_path):
        with open(file_path, 'r') as file:
            injuries_data = yaml.safe_load(file)
        return injuries_data

    def load_interventions(self, file_path):
        with open(file_path, 'r') as file:
            interventions_data = yaml.safe_load(file)
        return interventions_data

    def load_merts(self, file_path):
        with open(file_path, 'r') as file:
            merts_data = yaml.safe_load(file)
        return merts_data

    def load_patients(self, file_path):
        with open(file_path, 'r') as file:
            patients_data = yaml.safe_load(file)
        return patients_data

    def create_patients_dict(self, patients_data, injuries_data):
        patients_dict = {}

        # Iterate through patients to extract required info
        for patient in patients_data['patients']:
            patient_name = patient['first_name'] + ' ' + patient['last_name']

            # Extract the latest triage score and category
            triage_data = patient['patient_record']['triage_category'][-1]
            triage_score = triage_data['triage_score']
            triage_category = triage_data['triage_category']

            required_resources = set()

            # Iterate through injuries and extract interventions and resources
            for injury_record in patient['patient_record']['injuries']:
                injury_id = injury_record['injury_id']
                injury = next((inj for inj in injuries_data['injuries'] if inj['injury_id'] == injury_id), None)
                if injury:
                    for intervention in injury['interventions']:
                        for resource in intervention['resources']:
                            if resource['item']!= 'None':
                                required_resources.add((resource['item'], resource['qty']))

            # Store patient details
            patients_dict[patient_name] = {
                'triage_score': triage_score,
                'triage_category': triage_category,
                'required_resources': list(required_resources)
            }

        return patients_dict

    def create_available_resources_dict(self, merts_data):
        available_resources_dict = {}

        # Find MERT-VM-001 and extract resources
        mert_vm = next((mert for mert in merts_data['merts'] if mert['mert_id'] == 'MERT-VM-001'), None)
        if mert_vm:
            for resource in mert_vm['resources']:
                resource_name = resource['item']
                qty = resource['qty']
                available_resources_dict[resource_name] = qty

        return available_resources_dict

    def create_patients_dict_new(self, patients_data):
        patients_dict = {}

        # Iterate through patients to extract required info
        for patient in patients_data['patients']:
            patient_name = patient['first_name'] + ' ' + patient['last_name']

            # Extract the latest triage score and category
            triage_data = patient['patient_record']['triage_category'][-1]
            triage_score = triage_data['triage_score']
            triage_category = triage_data['triage_category']

            injuries = set()

            # Iterate through injuries and extract interventions and resources
            for injury_record in patient['patient_record']['injuries']:
                injury_id = injury_record['injury_id']
                injuries.add(injury_id)

            # Store patient details
            patients_dict[patient_name] = {
                'triage_score': triage_score,
                'triage_category': triage_category,
                'has_injuries': list(injuries)
            }

        return patients_dict

    def create_injuries_dict(self, injuries_data):
        injuries_dict = {}

        # Iterate through patients to extract required info
        for injury in injuries_data['injuries']:
            injury_id = injury['injury_id']
            injury_label = injury['label']

            interventions = set()
            for intervention in injury['interventions']:
                intervention_id = intervention['intervention_id']
                interventions.add(intervention_id)

            injuries_dict[injury_id] = {
                'injury_label': injury_label,
                'need_interventions': list(interventions)
            }
        return injuries_dict

    def create_interventions_dict(self, interventions_data):
        interventions_dict = {}

        # Iterate through patients to extract required info
        for intervention in interventions_data['interventions']:
            intervention_id = intervention['intervention_id']
            intervention_label = intervention['label']

            resources = set()
            for resource in intervention['resources']:
                resource_id = resource['item_id']
                resource_name = resource['item']
                resources.add(resource_name)

            interventions_dict[intervention_id] = {
                'intervention_label': intervention_label,
                'includes_resources': list(resources)
            }
        return interventions_dict