# Evaluating Patient Burns for AIS Severity Score

## Overview
Burn injuries are typically communicated as a body location and burn degree, eg. "Circumferential 2nd Degree Burn to Upper Left Arm."
However, many triage algorithms, like NISS and TRISS, require an AIS severity score for the burn injury that requires some math and is not always intuitive.
Burn AIS severity scores are determined by the body location group, burn degree, and total body surface area (TBSA) of the burn.
- See `AIS_mapping` in [domain_data/burn_injury_reference.yaml](domain_data/burn_injury_reference.yaml) for the mapping of burn locations and degrees to AIS severity scores.
- (See [AIS Severity Score for Burns](https://www.trauma.org/archive/scores/aisburn.html) for more information.)

This service automatically calculates the AIS severity scores for a patient's burn injuries given only the burn location, burn degree, and age of the patient as an optional parameter.

Thus, when given only the burn location, burn degree, and age as an optional parameter, this service:
- Calculates Total Body Surface Area (TBSA) based on the users' choice of either 'The Rule of 9's' or the more accurate 'Lund and Browder Chart', which factors in the patient's age and body proportions.
- Determines the body 

## How it Works
Other NLP services, will process a natural language statement and extract normalized data for processing.
For example, NL_statement: "Circumferential 2nd Degree Burn to Upper Left Arm" will be normalized as {injury_type: burn, burn_degree: 2nd Degree, location: arm, sublocation: upper, lateral_position: left, coronal_position: circumferential} and attached to the patient's record.  However, that statement and the resulting normalized data are not enough to calculate the AIS severity score for the burn injury without some math that we want to avoid in high-stress and masscal situations. Therefore, this service can be invoked to calculate the AIS severity score for the burn injuries.

### Helper Functions
`get_burn_tbsa` - Calculates the Total Body Surface Area (TBSA) of a burn injury based on the user's choice of either 'The Rule of 9's' or the more accurate 'Lund and Browder Chart', which factors in the patient's age and body proportions.

`group_burns_by_location` - Returns a body_part_group, either 'Head_Neck_Hands_Feet' or 'Limbs_Torso', based on the burn injury location.

`get_burn_ais_severity` - Returns the AIS severity score for a burn injury based on the burn body_part_group, burn_degree, and total_TBSA.

### Main Function
`evaluate_patient_burns` - Evaluates the AIS severity scores for a single patient's burn injuries given only the burn location, burn degree, and age as an optional parameter.
`evaluate_all_patients_burns` - Evaluates the AIS severity scores for all patients' burn injuries given only the burn location, burn degree, and age as an optional parameter.  This function is useful for mass casualty incident triage.

## Testing
To test the service, navigate to the `tests/services/evaluate_patient_burns` directory and run the following command:
```bash
pytest test_evaluate_patient_burns.py
```

## Usage
To use the service, import the `evaluate_patient_burns` function from the `evaluate_patient_burns.py` file and pass in the patient_state's patient_record.insults, and age as an optional parameter.  The function will return the AIS severity score for the burn injury. 
<!-- TODO  -->

```python
