
from services.service_adaptive_resource_opt.ServiceAdaptiveResourceOpt import AdaptiveResourceOptMethods
from services.service_adaptive_resource_opt.algos.helpers import Helper
from services.service_adaptive_resource_opt.algos.data_loader import DataLoader
class AdaptiveResourceOpt(AdaptiveResourceOptMethods):

    def __init__(self):
        self.helper = Helper()
        self.data_loader = DataLoader()


    def optimal_resource_management(self, data_dir):
        patients_dict, injuries_dict, interventions_dict, available_resources_dict = self.data_loader.load_data_new(data_dir=data_dir)
        patients, patients_scores, patient_requirements, resources, resource_availability, final_criteria = self.helper.initialize_pyreason(
            patients_dict=patients_dict, injuries_dict=injuries_dict, interventions_dict=interventions_dict, available_resources_dict=available_resources_dict)
        # patients_dict, available_resources_dict = self.data_loader.load_data(data_dir=data_dir)
        # patients, patients_scores, patient_requirements, resources, resource_availability, final_criteria = self.helper.initialize_pyreason(patients_dict=patients_dict, available_resources_dict=available_resources_dict)
        served_patients = self.helper.run_opt(patients=patients, patients_scores=patients_scores, patient_requirements=patient_requirements, resources=resources, resource_availability=resource_availability, final_criteria=final_criteria)
        self.helper.update_pyreason_facts(patients=patients, patients_scores=patients_scores, patient_requirements=patient_requirements, resources=resources, resource_availability=resource_availability, served_patients=served_patients)






