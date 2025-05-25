from services.models.ModelPatient import Patient
from services.models.ModelPatientMatrix import PatientMatrix

class PatientPriority:
    def return_patient_priority_matrix(self, patients_categories: list[Patient]) -> list[PatientMatrix]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")