from services.service_triage.AlgoTriage import Triage

from services.models.ModelTriageScore import TriageScore, RationaleRecord, Vital
from services.models.ModelPatient import Patient
from datetime import datetime


class BasicTriage2(Triage):

    def __init__(self, thresholds):
        self.thresholds = thresholds

    def triage(self, patient: Patient) -> TriageScore:
        record = patient.physiology_record
        rationale_records = []
        score = 0.0

        if not record:
            return TriageScore(score=0.0, rationale=rationale_records, datetime_seconds=int(datetime.now().timestamp()),
                               algo_name="BasicTriage")



        for vital_name, threshold in self.thresholds.items():
            if vital_name in record:

                if vital_name == "gcs":
                    value = record[vital_name]
                    if value < threshold.min_value:
                        score += 50.0

                        rationale_records.append(RationaleRecord(vital=Vital(name=vital_name, value=value), score=5.0,
                                                             threshold=threshold))



        # Return the TriageScore with the total score, rationale, datetime, and algorithm name
        return TriageScore(
            datetime_seconds=int(datetime.now().timestamp()),
            algo_name="BasicTriageAlgo2",
            score=score,
            confidence=1,
            rationale=rationale_records
        )