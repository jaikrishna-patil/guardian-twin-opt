import time

from services.service_patient_priority_matrix.factory.FactoryAlgo import TriagecategoryToPatientmatrixFactory, Threshold
from services.service_patient_priority_matrix.factory.FactoryAlgo import TriagecategoryToPatientMatrixAlgoName
from services.models.ModelPatient import Patient

import pandas as pd
import pyreason as pr
import os
import numba

if __name__ == "__main__":



    patient1_cat = Patient(name='Adrian Monk', category='immediate')
    patient2_cat = Patient(name='Natalie Tieger', category='immediate')
    patient3_cat = Patient(name='Leland Stottlemeyer', category='immediate')
    patient4_cat = Patient(name='Jake Peralta', category='expectant')
    patient5_cat = Patient(name='Sharona Fleming', category='delayed')

    patient6_cat = Patient(name='Randy Disher', category='expectant')
    patient7_cat = Patient(name='Trudy Monk', category='immediate')
    patient8_cat = Patient(name='Charles Kroger', category='minor')
    patient9_cat = Patient(name='Julie Trieger', category='delayed')
    patient10_cat = Patient(name='Benjy Fleming', category='delayed')
    all_patients_cat = [patient1_cat, patient2_cat, patient3_cat, patient4_cat, patient5_cat, patient6_cat, patient7_cat, patient8_cat, patient9_cat, patient10_cat]

    print("")
    print("ALGO :: Patients Triage categories -> Patients priority matrix")
    algo_patient_matrix = TriagecategoryToPatientmatrixFactory.create_triageCategory_to_patientMatrix_algo(mode=TriagecategoryToPatientMatrixAlgoName.BASIC)
    matrix_all_patients = algo_patient_matrix.return_patient_priority_matrix(all_patients_cat)
    for matrix_patient in matrix_all_patients:
        print('\n')
        print(f"Patient {matrix_patient.patient_name} has the following priority details: {matrix_patient}")



