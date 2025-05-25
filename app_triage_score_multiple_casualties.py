import time

from services.service_triage.factory.FactoryAlgoTriage import TriageFactory, Threshold
from services.service_triage.factory.FactoryAlgoTriage import TriageAlgoName
from services.models.ModelPatient import Patient

import pandas as pd
import pyreason as pr
import os
import numba

if __name__ == "__main__":

    thresholds_data_algo3 = {
        'external_hemorrhage': Threshold(min_value=1, max_value=6),
        'tension_pneumothorax': Threshold(min_value=1, max_value=6),
        'traumatic_brain_injury': Threshold(min_value=1, max_value=6),
        'concussion': Threshold(min_value=1, max_value=6),
        'cerebral_contusion': Threshold(min_value=1, max_value=6),
        'subarachnoid_hemorrhage': Threshold(min_value=1, max_value=6),
        'epidural_hematoma': Threshold(min_value=1, max_value=6),
        'nasal_fracture': Threshold(min_value=1, max_value=6),
        'orbital_fracture': Threshold(min_value=1, max_value=6),
        'le_fort_II_fracture': Threshold(min_value=1, max_value=6),
        'rib_fracture': Threshold(min_value=1, max_value=6),
        'lung_contusion': Threshold(min_value=1, max_value=6),
        'flail_chest': Threshold(min_value=1, max_value=6),
        'aortic_laceration': Threshold(min_value=1, max_value=6),
        'minor_liver_laceration': Threshold(min_value=1, max_value=6),
        'splenic_laceration': Threshold(min_value=1, max_value=6),
        'liver_hematoma': Threshold(min_value=1, max_value=6),
        'pancreatic_transection': Threshold(min_value=1, max_value=6),
        'radius_ulna_fracture': Threshold(min_value=1, max_value=6),
        'femur_fracture': Threshold(min_value=1, max_value=6),
        'knee_dislocation': Threshold(min_value=1, max_value=6),
        'traumatic_amputation_below_knee': Threshold(min_value=1, max_value=6),
        'traumatic_amputation_above_knee': Threshold(min_value=1, max_value=6),
        'burn': Threshold(min_value=1, max_value=6),
        'gcs': Threshold(min_value=3, max_value=15),
        'sbp': Threshold(min_value=0, max_value=219),
        'rr': Threshold(min_value=0, max_value=100),
    }


    patient1 = Patient(name='Adrian Monk', external_hemorrhage=3, tension_pneumothorax=4,traumatic_brain_injury=6, burn=2,
                       gcs=10, sbp=60, rr=20)
    patient2 = Patient(name='Natalie Tieger', splenic_laceration=6,
                       gcs=6, sbp=100, rr=40)
    patient3 = Patient(name='Leland Stottlemeyer', external_hemorrhage=5, burn=6)
    patient4 = Patient(name='Jake Peralta', liver_hematoma=4, tension_pneumothorax=6,
                       traumatic_brain_injury=4, burn=6,
                       gcs=5, sbp=120, rr=88)
    patient5 = Patient(name='Sharona Fleming', gcs=12, sbp=120, rr=89)

    patient6 = Patient(name='Randy Disher', external_hemorrhage=5, tension_pneumothorax=6, traumatic_brain_injury=6,
                       burn=2,
                       gcs=15, sbp=80, rr=60)
    patient7 = Patient(name='Trudy Monk', splenic_laceration=6,
                       gcs=6, sbp=100, rr=40)
    patient8 = Patient(name='Charles Kroger', external_hemorrhage=2, burn=1)
    patient9 = Patient(name='Julie Trieger', liver_hematoma=1, tension_pneumothorax=1,
                       traumatic_brain_injury=1, burn=1,
                       gcs=4, sbp=40, rr=20)
    patient10 = Patient(name='Benjy Fleming', gcs=12, sbp=120, rr=89)
    all_patients = [patient1, patient2, patient3, patient4, patient5, patient6, patient7, patient8, patient9, patient10]
    # Triage Algo 3 - Patient 3
    print("")
    print("ALGO 3- LIFETriage")
    triage_life_algo = TriageFactory.create_triage_algo(TriageAlgoName.LIFE, thresholds=thresholds_data_algo3)
    triage_score_all_patients = triage_life_algo.triage(all_patients)
    for triage_score_patient in triage_score_all_patients:
        print('\n\n')
        print(f"Patient has the following LIFE Triage Scores {triage_score_patient}")



