import time

from services.service_triage_category.factory.FactoryAlgo import TriagescoreToTriagecategoryFactory, Threshold
from services.service_triage_category.factory.FactoryAlgo import TriagescoreToTriagecategoryAlgoName
from services.models.ModelPatient import Patient

import pandas as pd
import pyreason as pr
import os
import numba

if __name__ == "__main__":

    thresholds_data = {
        'triage_score': Threshold(min_value=0, max_value=100)
    }


    patient1 = Patient(name='Adrian Monk', triage_score=33)
    patient2 = Patient(name='Natalie Tieger', triage_score=40)
    patient3 = Patient(name='Leland Stottlemeyer', triage_score=43)
    patient4 = Patient(name='Jake Peralta', triage_score=20)
    patient5 = Patient(name='Sharona Fleming', triage_score=87)

    patient6 = Patient(name='Randy Disher', triage_score=1)
    patient7 = Patient(name='Trudy Monk', triage_score=40)
    patient8 = Patient(name='Charles Kroger', triage_score=95)
    patient9 = Patient(name='Julie Trieger', triage_score=80)
    patient10 = Patient(name='Benjy Fleming', triage_score=87)
    all_patients = [patient1, patient2, patient3, patient4, patient5, patient6, patient7, patient8, patient9, patient10]

    print("")
    print("ALGO :: Triage scores -> Triage categories")
    algo_triage_categories = TriagescoreToTriagecategoryFactory.create_triageScore_to_triageCategory_algo(mode=TriagescoreToTriagecategoryAlgoName.BASIC, thresholds=thresholds_data)
    triage_category_all_patients = algo_triage_categories.return_triage_categories(all_patients)
    for triage_category_patient in triage_category_all_patients:
        print('\n')
        print(f"Patient {triage_category_patient.patient_name} has the following triage category {triage_category_patient}")



