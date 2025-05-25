from services.models.ModelPatient import Patient
from services.models.ModelTriageCategory import TriageCategory


class Triage:
    def return_triage_categories(self, patients: list[Patient]) -> list[TriageCategory]:
        raise NotImplementedError("Subclasses must implement triage score to triage category method.")