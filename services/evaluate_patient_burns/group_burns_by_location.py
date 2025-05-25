# PURPOSE: Group burn injuries by location and assign a body part group to each burn injury.
# INPUTS:
# - insult: A dictionary containing the following fields:
#     - location: A string representing the location of the burn injury
#     - sublocation: A string representing the sublocation of the burn injury
# OUTPUTS:
# - body_part_group: A string representing the body part group of the burn injury: Head_Neck_Hands_Feet or Limbs_Torso

import logging
from flask import Flask, request, jsonify

from gt_service_tools.services.evaluate_patient_burns.get_burn_reference_data import GetBurnReferenceData

app = Flask(__name__)

class GroupBurnsByLocation:
    def __init__(self):
        self.get_burn_reference_data = GetBurnReferenceData()
        self.body_part_groups = self.get_burn_reference_data.get_body_part_groups()
        self.patient_state = {}
        
    def set_patient_state(self, patient_state):
        self.patient_state = patient_state
        return self.patient_state
    
    def get_location_group_for_burn(self, insult):
        """
        AIS Severity Scoring requires the body part group for a burn insult based on the location and sublocation of the insult.
        This method gets the body part group for a burn insult based on the location and sublocation of the insult.
        For example, if the location is 'Head', the body part group would be 'Head_Neck_Hands_Feet'.
        If the location is 'Arm' and the sublocation is 'Hand', the body part group would be 'Head_Neck_Hands_Feet'.
        If the location is 'Arm' and the sublocation is 'Upper', the body part group would be 'Limbs_Torso'.

        Args:
            insult (dict): The burn insult containing the location and sublocation of the burn injury.

        Raises:
            ValueError: Missing location for the burn insult.
            ValueError: Missing sublocation for the burn insult.
            ValueError: Invalid location for the burn insult.

        Returns:
            string: The body part group for the burn insult.
        """
        logging.debug(f"get_location_group_for_burn insult: {insult}")
        
        sublocation = insult.get('sublocation')
        
        location = insult.get('location')
        if not location:
            raise ValueError(f"Missing location for insult {insult}.")
        location = location.lower()
        
        if sublocation:
            sublocation = sublocation.lower()
        
        if sublocation in {'hand', 'foot'}:
            location = sublocation
        
        body_part_group = next((group for group, locations in self.body_part_groups.items() if location in locations), None)
        if not body_part_group:
            raise ValueError(f"Invalid location '{location}' for insult {insult}.")
        
        return body_part_group

    
    # Iterates through the insults in the patient state and adds the body_part_group to each insult
    # TODO: Add error handling for missing location
    # TODO: Add error handling for invalid location
    # TODO: Add error handling for missing sublocation
    # TODO: Add error handling for invalid sublocation
    def set_location_groups_for_burns(self):
        updated_patient_state = self.patient_state
        insults = updated_patient_state.get('insults', [])
        for insult in insults:
            insult_label = insult.get('label')
            if insult_label:
                insult_label = insult_label.lower()
            else:
                raise ValueError(f"Missing Insult label for {insult}.")
            if insult_label in ['thermal burn', 'burn']:
                body_part_group = self.get_location_group_for_burn(insult)
            insult['body_part_group'] = body_part_group
        updated_patient_state['insults'] = insults
        return updated_patient_state
    
    



if __name__ == '__main__':
    app.run(debug=True)