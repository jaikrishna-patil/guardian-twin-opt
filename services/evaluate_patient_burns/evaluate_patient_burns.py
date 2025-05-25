from datetime import datetime
from gt_service_tools.services.evaluate_patient_burns.group_burns_by_location import GroupBurnsByLocation 
from gt_service_tools.services.evaluate_patient_burns.get_burn_tbsa import GetBurnTBSA
from gt_service_tools.services.evaluate_patient_burns.get_burn_AIS_severity import GetBurnAISSeverity

class EvaluatePatientBurns:
    def __init__(self):
        self.group_burns_by_location = GroupBurnsByLocation()
        self.get_burn_tbsa = GetBurnTBSA()
        self.get_burn_ais_severity = GetBurnAISSeverity()
        self.reset()

    def reset(self):
        self.patient_insults = []
        self.burn_injury_groups = []
        self.burn_algorithm = 'rule_of_nines'
        self.patient_age = None

    def evaluate_burn_injuries(self, patient_insults, tbsa_algo, patient_age):
        self.patient_insults = patient_insults
        self.patient_age = patient_age
        self.burn_algorithm = tbsa_algo or self.burn_algorithm

        for insult in self.patient_insults:
            self.process_insult(insult)

    def process_insult(self, insult):
        try:
            body_part_group = self.group_burns_by_location.get_location_group_for_burn(insult)
            insult['body_part_group'] = body_part_group
            tbsa = self.get_burn_tbsa.get_tbsa_from_location(insult, self.burn_algorithm, self.patient_age)
            insult['tbsa'] = float(tbsa)
        except ValueError as e:
            raise ValueError(f"ValueError: {e}")
        except Exception as e:
            raise Exception(f"Exception: {e}")

    def create_burn_injury_groups(self):
        burn_injury_groups = {}

        for insult in self.patient_insults:
            key = (insult['body_part_group'], insult['burn_degree'])
            if key not in burn_injury_groups:
                burn_injury_groups[key] = self.initialize_burn_injury_group(insult)
            self.update_burn_injury_group(burn_injury_groups[key], insult)

        self.burn_injury_groups = list(burn_injury_groups.values())

    def initialize_burn_injury_group(self, insult):
        return {
            'timestamp': datetime.now().isoformat(),
            'label': 'Thermal Burn Injury Group',
            'body_part_group': insult['body_part_group'],
            'burn_degree': insult['burn_degree'],
            'burn_algorithm': self.burn_algorithm,
            'total_tbsa': 0,
            'AIS_severity_score': None,
            'insults': []
        }

    def update_burn_injury_group(self, burn_injury_group, insult):
        burn_injury_group['total_tbsa'] += insult['tbsa']
        burn_injury_group['insults'].append(insult)

    def calculate_ais_severity_scores(self):
        for burn_injury_group in self.burn_injury_groups:
            burn_injury_group['AIS_severity_score'] = self.get_burn_ais_severity.get_ais_severity_score(burn_injury_group)

    def update_patient_insults(self):
        return [
            {
                'timestamp': group['timestamp'],
                'label': group['label'],
                'body_part_group': group['body_part_group'],
                'burn_degree': group['burn_degree'],
                'burn_algorithm': group['burn_algorithm'],
                'total_tbsa': group['total_tbsa'],
                'AIS_severity_score': group['AIS_severity_score'],
                'insults': group['insults']
            }
            for group in self.burn_injury_groups
        ]

    def evaluate_patient_burns(self, patient_insults=None, tbsa_algo=None, patient_age=None):
        try:
            self.evaluate_burn_injuries(patient_insults, tbsa_algo, patient_age)
            self.create_burn_injury_groups()
            self.calculate_ais_severity_scores()
            updated_patient_insults = self.update_patient_insults()
            self.reset()
            return updated_patient_insults
        except ValueError as e:
            raise ValueError(f"ValueError: {e}")
        except Exception as e:
            raise Exception(f"Exception: {e}")