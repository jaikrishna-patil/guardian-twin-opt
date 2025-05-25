import time

from services.service_mission_options_care_facilities.factory.FactoryAlgo import MissionrequirementsToMissionoptionsCFsFactory
from services.service_mission_options_care_facilities.factory.FactoryAlgo import MissionrequirementsToMissionoptionsCFsAlgoName
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelCareFacility import CareFacility

import pandas as pd
import pyreason as pr
import os
import numba

if __name__ == "__main__":



    mission1 = MissionRequirements(name='Adrian Monk', required_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=['trauma_surgery', 'emergency_medicine', 'orthopedic_surgery', 'general_surgery'], required_medical_supplies=['blood_bags', 'painkillers', 'antibiotics', 'anesthetics'])
    mission2 = MissionRequirements(name='Natalie Tieger', required_medical_services=['medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=['general_surgery'], required_medical_supplies=['blood_bags', 'painkillers'])
    mission3 = MissionRequirements(name='Leland Stottlemeyer', required_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=[], required_medical_supplies=['blood_bags', 'antibiotics', 'anesthetics'])
    mission4 = MissionRequirements(name='Jake Peralta', required_medical_services=[],
                                   required_medical_specialities=['general_surgery'], required_medical_supplies=['blood_bags', 'antibiotics', 'anesthetics'])
    mission5 = MissionRequirements(name='Sharona Fleming', required_medical_services=['surgical_services', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=['trauma_surgery', 'emergency_medicine', 'orthopedic_surgery', 'general_surgery'], required_medical_supplies=['blood_bags', 'painkillers', 'antibiotics', 'anesthetics'])

    mission6 = MissionRequirements(name='Randy Disher', required_medical_services=['emergency_care', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=['trauma_surgery', 'emergency_medicine'], required_medical_supplies=['blood_bags'])
    mission7 = MissionRequirements(name='Trudy Monk', required_medical_services=['emergency_care', 'surgical_services'],
                                   required_medical_specialities=['trauma_surgery', 'general_surgery'], required_medical_supplies=['blood_bags', 'painkillers', 'antibiotics', 'anesthetics'])
    mission8 = MissionRequirements(name='Charles Kroger', required_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=[ 'orthopedic_surgery', 'general_surgery'], required_medical_supplies=['blood_bags', 'painkillers', 'antibiotics', 'anesthetics'])
    mission9 = MissionRequirements(name='Julie Trieger', required_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=['trauma_surgery', 'emergency_medicine'], required_medical_supplies=[])
    mission10 = MissionRequirements(name='Benjy Fleming', required_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   required_medical_specialities=['trauma_surgery', 'emergency_medicine', 'orthopedic_surgery', 'general_surgery'], required_medical_supplies=[])

    cf1 = CareFacility(cf_name = 'Battlefield Medical Center', cf_bed_capacity=50, available_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   available_medical_specialities=['trauma_surgery', 'emergency_medicine', 'orthopedic_surgery', 'general_surgery'], available_medical_supplies=['blood_bags', 'painkillers', 'antibiotics', 'anesthetics'])

    cf2 = CareFacility(cf_name = 'Noble Medical Center', cf_bed_capacity=20, available_medical_services=['medical_imaging', 'laboratory_services'],
                                   available_medical_specialities=['emergency_medicine', 'orthopedic_surgery', 'general_surgery'], available_medical_supplies=['blood_bags', 'painkillers', 'anesthetics'])

    cf3 = CareFacility(cf_name = 'Young hearts Medical Center', cf_bed_capacity=10, available_medical_services=['emergency_care', 'surgical_services', 'medical_imaging', 'laboratory_services'],
                                   available_medical_specialities=['trauma_surgery', 'emergency_medicine', 'orthopedic_surgery', 'general_surgery'], available_medical_supplies=[])

    all_mission_reqs = [mission1, mission2, mission3, mission4, mission5, mission6, mission7, mission8, mission9, mission10]
    all_cfs = [cf1, cf2, cf3]
    print("")
    print("ALGO :: Mission requirements -> Mission options care facilites")
    algo_mission_cfs = MissionrequirementsToMissionoptionsCFsFactory.create_missionrequirements_to_missionoptionsCFs_algo(mode=MissionrequirementsToMissionoptionsCFsAlgoName.BASIC)
    cfs_all_missions = algo_mission_cfs.return_mission_options_care_facilities(mission_requirements=all_mission_reqs, care_facilities=all_cfs)
    for mission in cfs_all_missions:
        print('\n')
        print(f"Patient {mission.patient_name} can be assigned following Care facilities: {mission}")



