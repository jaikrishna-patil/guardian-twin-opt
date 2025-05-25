import numpy as np
from services.models.ModelPatient import Patient
from services.models.ModelTriageScore import TriageScore

from services.service_triage_interaction.TriageInteraction import TriageWithInteraction


class BasicTriageWithInteraction(TriageWithInteraction):
    def triage(self, patient: Patient) -> TriageScore:
        input_data = {
            "datetime_seconds": 1623584076,
            "algo_name": "Example Algorithm",
            "score": 8.5,
            "confidence": 0.9,
            "rationale": [
                {
                    "score": 8.0,
                    "vital": {
                        "name": "Heart Rate",
                        "value": 80
                    },
                    "threshold": 70
                },
                {
                    "score": 9.0,
                    "vital": {
                        "name": "Oxygen Saturation",
                        "value": 95
                    },
                    "threshold": 90
                }
            ],
            "interaction": {
                "question": "GCS value is missing. Do you want to enter estimated value for GCS? (y/n), if not then default (15) is used:",
                "options": [
                    {
                        "input": "Y",
                        "description": "Numerical values between 0 and 13 for GCS"
                    },
                    {
                        "input": "N",
                        "description": "Typing N, Means No, so a value of 15 will be used"
                    }
                ]
            }
        }

        obj = TriageScore(**input_data)

        return obj


