from services.models.ModelPatient import Patient
from services.models.ModelTriageScore import TriageScore


class Triage:
    def triage(self, patients: list[Patient]) -> list[TriageScore]:
        raise NotImplementedError("Subclasses must implement triage method.")