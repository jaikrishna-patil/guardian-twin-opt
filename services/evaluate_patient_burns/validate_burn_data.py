# PURPOSE: Validate burn injury data provided by the user

from gt_service_tools.services.evaluate_patient_burns.get_burn_reference_data import GetBurnReferenceData

class ValidateBurnData:
    def __init__(self):
        self.get_burn_reference_data = GetBurnReferenceData()
        self.valid_burn_location_data = self.get_burn_reference_data.get_valid_burn_location_data()
        self.tbsa_algorithms = self.get_burn_reference_data.get_burn_tbsa_algos()

    # Ensures the TBSA algorithm is enabled and exists in the burn_tbsa_algorithms reference data
    def validate_tbsa_algorithm(self, tbsa_algorithm):
        if not tbsa_algorithm:
            return 'rule_of_nines'
        else:
            tbsa_algorithm = tbsa_algorithm.lower()
            for algorithm in self.tbsa_algorithms:
                if algorithm['name'] == tbsa_algorithm:
                    if algorithm['user_settings']['enabled']:
                        return tbsa_algorithm
                    else:
                        raise ValueError(f"Algorithm {tbsa_algorithm} is not enabled.")
            raise ValueError("Invalid TBSA algorithm.")

    # Ensures the burn location is provided and is a valid location in the burn_injury_reference data
    def validate_location(self, burn_injury_data):
        location = burn_injury_data.get('location')
        if not location:
            raise ValueError("Burn location is required.")
        location = location.capitalize()
        if location not in self.valid_burn_location_data:
            raise ValueError(f"Invalid burn location: {location}")
        return location

    # Ensures the burn sublocation is provided and is a valid sublocation of the given location in the burn_injury_reference data
    def validate_sublocation(self, burn_injury_data, location):
        sublocation = burn_injury_data.get('sublocation')
        if not sublocation:
            sublocation = "Entire"
        sublocation = sublocation.capitalize()
        if sublocation not in self.valid_burn_location_data[location]:
            raise ValueError(f"Invalid burn sublocation: {sublocation}")
        return sublocation

    # Ensures the coronal plane is provided and is a valid coronal plane of the given location and sublocation in the burn_injury_reference data
    def validate_coronal_position(self, burn_injury_data, location, sublocation):
        coronal_position = burn_injury_data.get('coronal_position')
        if location in ['Arm', 'Leg']:
            if not coronal_position:
                raise ValueError(f"Coronal position is required for {location} burns.")
            coronal_position = coronal_position.capitalize()
            if coronal_position not in self.valid_burn_location_data[location][sublocation]:
                raise ValueError(f"Invalid coronal plane: {coronal_position}")
            return coronal_position
        else:
            if coronal_position is not None:
                raise ValueError(f"Coronal plane is not required for {location} burns.")
        return None
    
    # Ensures the age is provided and is an integer between 0 and 120
    def validate_age(self, age):
        if age is None:
            return None
        try:
            age = float(age)
            if not (0 <= age <= 120):
                raise ValueError("Age must be between 0 and 120.")
            age = int(age)  # Convert to integer by rounding down
        except ValueError:
            raise ValueError("Age must be a number between 0 and 120.")
        return age
    
    # Validates the burn injury data provided. Ensures the location, sublocation, coronal plane, and age are provided. 
    # Ensures the location, sublocation, and coronal plane are valid names relative to each other.
    # eg. Arm.Upper.Circumferential == OK while Head.Upper.Anterior == Not OK because Head does not have an Upper sublocation in the reference data.
    # Called in get_burn_tbsa_from_location function in get_burn_tbsa.py
    def validate_burn_injury_data(self, burn_injury_data, age):
        location = self.validate_location(burn_injury_data)
        sublocation = self.validate_sublocation(burn_injury_data, location)
        coronal_position = self.validate_coronal_position(burn_injury_data, location, sublocation)
        age = self.validate_age(age)
        
        return location, sublocation, coronal_position, age
