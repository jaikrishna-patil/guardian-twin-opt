# PURPOSE: Get the AIS severity score for a burn injury group using the AIS mapping from the burn reference data, tbsa, and burn degree
# INPUTS:
# - burn_injury_group: A dictionary containing the following fields:
#     - body_part_group: A string representing the body part group of the burn injury
#     - total_tbsa: A number representing the total TBSA of the burn injury
#     - burn_degree: A string representing the degree of the burn injury
# OUTPUTS:
# - AIS_severity_score: A number representing the AIS severity score of the burn injury group (1-6)


from flask import Flask
from gt_service_tools.services.evaluate_patient_burns.get_burn_reference_data import GetBurnReferenceData
from gt_service_tools.services.evaluate_patient_burns.validate_burn_data import ValidateBurnData

app = Flask(__name__)

class GetBurnAISSeverity:
    def __init__(self):
        self.validate_burn_data = ValidateBurnData()
        self.get_burn_reference_data = GetBurnReferenceData()
        self.AIS_mapping = self.get_burn_reference_data.get_AIS_mapping()
        self.body_part_groups = self.get_burn_reference_data.get_body_part_groups()
    
    
    def validate_burn_injury_group(self, burn_injury_group):
        body_part_group = burn_injury_group["body_part_group"]
        total_tbsa = burn_injury_group["total_tbsa"]
        burn_degree = burn_injury_group["burn_degree"]
        
        required_fields = [body_part_group, total_tbsa, burn_degree]
        for field in required_fields:
            if field is None:
                raise ValueError(f"Missing required field: {field}")
            
        if isinstance(total_tbsa, str):
            try:
                total_tbsa = float(total_tbsa)
            except ValueError:
                raise ValueError("total_tbsa must be a number")
        
        if not isinstance(body_part_group, str):
            raise ValueError("body_part_group must be a string")
        if not isinstance(burn_degree, str):
            raise ValueError("burn_degree must be a string")
        
        return body_part_group, total_tbsa, burn_degree
    
    def get_ais_severity_score(self, burn_injury_group):
        body_part_group, total_tbsa, burn_degree = self.validate_burn_injury_group(burn_injury_group)
        # print(f"Body Part Group: {body_part_group}")
        # print(f"Total TBSA: {total_tbsa}")
        # print(f"Burn Degree: {burn_degree}")
        for item in self.AIS_mapping:
            # print(f"Item: {item}")
            body_part_groups = item["body_part_groups"]
            if body_part_group in body_part_groups:
                degrees = body_part_groups[body_part_group]
                # print(f"Degrees: {degrees}")
                if burn_degree in degrees:
                    tbsa_range = degrees[burn_degree]
                    # print(f"TBSA Range: {tbsa_range}")
                    if tbsa_range[0] <= total_tbsa <= tbsa_range[1]-0.5: # 0.5 is used to make the tbsa ranges easier to read, but make the function jump to higher AIS if the tbsa is at the top of the range
                        # print(f"AIS Severity Score: {item['AIS_severity_score']}")
                        return item["AIS_severity_score"]
        
        raise ValueError("No matching AIS severity score found for the provided burn injury group")