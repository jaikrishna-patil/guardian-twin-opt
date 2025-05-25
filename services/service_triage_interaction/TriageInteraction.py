from services.models.ModelPatient import Patient
from services.models.ModelTriageScore import TriageScore
from services.models.ModelTriageScore import TriageScore


class TriageWithInteraction:
    def triage(self, patient: Patient) -> TriageScore:
        raise NotImplementedError("Subclasses must implement triage method.")