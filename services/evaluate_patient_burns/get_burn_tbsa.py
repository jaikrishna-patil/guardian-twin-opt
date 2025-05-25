# PURPOSE: Get the TBSA value for a burn injury using the burn reference data and the selected TBSA algorithm
# INPUTS:
# - burn_injury_data: A dictionary containing the following fields:
#     - location: A string representing the location of the burn injury
#     - sublocation: A string representing the sublocation of the burn injury
#     - coronal_position: A string representing the coronal position of the burn injury
#     - age: An integer representing the age of the patient
# - tbsa_algorithm: A string representing the TBSA algorithm to use (default: 'rule_of_nines') or lund_and_browder (which requires age)
# OUTPUTS:
# - tbsa: A number representing the TBSA percent of the burn injury

from flask import Flask
from gt_service_tools.services.evaluate_patient_burns.get_burn_reference_data import GetBurnReferenceData
from gt_service_tools.services.evaluate_patient_burns.validate_burn_data import ValidateBurnData

app = Flask(__name__)

class GetBurnTBSA:
    def __init__(self):
        self.validate_burn_data = ValidateBurnData()
        self.get_burn_reference_data = GetBurnReferenceData()
        self.tbsa_data = self.get_burn_reference_data.get_tbsa_data()
        self.tbsa_algorithms = self.get_burn_reference_data.get_burn_tbsa_algos()
        self.valid_burn_location_data = self.get_burn_reference_data.get_valid_burn_location_data()
    
    # Get TBSA using Lund Browder method, which adjusts TBSA based on age
    def get_tbsa_using_lund_browder(self, base_path, age, tbsa):
        if 'tbsa_by_age_range' in base_path:
            tbsa_by_age_range = base_path['tbsa_by_age_range']
            tbsa = None
            if age:
                for tbsa_percentage, age_range in tbsa_by_age_range.items():
                    min_age = age_range[0]
                    max_age = age_range[1]
                    if min_age <= age <= max_age:
                        tbsa = tbsa_percentage
                        break
                else:
                    raise ValueError(f"Age {age} is not within a valid age range.")
        return tbsa
    
    # Validate the location and sublocation and get the base path for the TBSA data
    def validate_and_get_base_path(self, location, sublocation):
        base_path = self.tbsa_data.get(location, {}).get(sublocation)
        if not base_path:
            raise ValueError(f"{location}.{sublocation} not found in tbsa_by_location reference data.")
        return base_path

    # Get the TBSA value from the base path using the selected TBSA algorithm
    def get_tbsa(self, base_path, coronal_plane, tbsa_algorithm, age):
        tbsa_algorithm = tbsa_algorithm.lower()
        lund_and_browder = ['lund_and_browder', 'browder_and_lund',  'lund_browder', 'browder_lund']
        if tbsa_algorithm in lund_and_browder and age is None:
            raise ValueError("Age is required for Lund Browder algorithm.")
        
        tbsa_path = base_path.get(coronal_plane) if coronal_plane and base_path.get(coronal_plane) else base_path
        tbsa = tbsa_path['tbsa']
        
        if tbsa_algorithm == 'lund_and_browder':
            tbsa = self.get_tbsa_using_lund_browder(tbsa_path, age, tbsa)
        
        return tbsa

    # Main function - Get the TBSA value from the burn injury data using the selected TBSA algorithm
    def get_tbsa_from_location(self, burn_injury_data, tbsa_algorithm, age):
        print(f"burn_injury_data: {burn_injury_data}")
        print(f"tbsa_algorithm: {tbsa_algorithm}")
        print(f"age: {age}")
        try:
            location, sublocation, coronal_plane, age = self.validate_burn_data.validate_burn_injury_data(burn_injury_data, age)
        except ValueError as e:
            raise

        try:
            tbsa_algorithm = self.validate_burn_data.validate_tbsa_algorithm(tbsa_algorithm)
        except ValueError as e:
            raise

        if not tbsa_algorithm:
            tbsa_algorithm = 'rule_of_nines'

        base_path = self.validate_and_get_base_path(location, sublocation)

        try:
            tbsa = self.get_tbsa(base_path, coronal_plane, tbsa_algorithm, age)
        except KeyError:
            raise ValueError(f"No TBSA data found at {location}.{sublocation}.{coronal_plane} in tbsa_by_location reference data.")

        if tbsa is not None:
            tbsa = float(tbsa.replace('%', ''))

        return tbsa
    
    
    
    
    # TODO: Write function and tests to get AIS severity score from TBSA and Burn Degree and Burn Location
    # TODO: Write normalization function to convert alternative location, sublocation, and coronal plane names or phrases to referencable location, sublocation, coronal_plane names