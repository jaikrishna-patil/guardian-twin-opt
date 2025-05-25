# PURPOSE: Get the burn reference data from the burn_injury_reference.yaml file
# TODO: Update to pull data from a database instead of a yaml file

import yaml
import os


## TODO: Update to pull data from a database instead of a yaml file
class GetBurnReferenceData:
    def __init__(self):
        # self.burn_reference_path = os.path.join('.', 'utils', 'medical', 'burn_injuries', 'burn_injury_reference.yaml') # Path relative to run.py in the gt_service_tools directory
        self.burn_reference_path = os.path.join(os.path.dirname(__file__),
                                                '../evaluate_patient_burns/domain_data/burn_injury_reference.yaml')
        self.burn_reference_data = self.get_burn_reference_data()

    def get_burn_reference_data(self):
        try:
            with open(self.burn_reference_path) as file:
                burn_reference_data = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise FileNotFoundError("Burn injury reference file not found")
        return burn_reference_data

        # Get the tbsa_by_location data from the burn injury reference data

    # Used for validating the burn injury data provided in the get_burn_tbsa_from_location function
    def get_tbsa_data(self):
        try:
            tbsa_data = self.burn_reference_data['tbsa_by_location']
            return tbsa_data
        except KeyError:
            raise KeyError("tbsa_by_location data not found in burn injury reference file")

    # Get the burn_tbsa_algorithms from the burn injury reference data
    # Used for validating the algorithm provided in the get_burn_tbsa_from_location function
    def get_burn_tbsa_algos(self):
        try:
            tbsa_algorithms = self.burn_reference_data['burn_tbsa_algorithms']
            return tbsa_algorithms
        except KeyError:
            raise KeyError("burn_tbsa_algorithms not found in burn injury reference file")

    def get_AIS_mapping(self):
        try:
            AIS_mapping = self.burn_reference_data['AIS_mapping']
            return AIS_mapping
        except KeyError:
            raise KeyError("AIS_mapping not found in burn injury reference file")

    def get_body_part_groups(self):
        try:
            body_part_groups = self.burn_reference_data['body_part_groups']
            return body_part_groups
        except KeyError:
            raise KeyError("body_part_groups not found in burn injury reference file")

    # Build a dictionary of valid burn locations, sublocations, and coronal planes based on the burn injury reference data
    # Used for validating the burn injury data provided in the get_burn_tbsa_from_location function
    def get_valid_burn_location_data(self):
        valid_burn_location_data = {}
        tbsa_data = self.get_tbsa_data()
        for location, sublocations in tbsa_data.items():
            valid_sublocations = {}
            for sublocation, coronal_planes in sublocations.items():
                if location in ['Arm', 'Leg'] and isinstance(coronal_planes, dict):
                    valid_coronal_planes = list(coronal_planes.keys())
                    valid_sublocations[sublocation] = valid_coronal_planes
                else:
                    valid_sublocations[sublocation] = []
            valid_burn_location_data[location] = valid_sublocations
        # print(f"Valid Burn Location Data: {valid_burn_location_data}")
        return valid_burn_location_data