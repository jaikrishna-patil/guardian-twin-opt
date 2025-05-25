import pandas as pd

from services.service_triage.AlgoTriage import Triage

from services.models.ModelTriageScore import TriageScore, RationaleRecord, Vital
from services.models.ModelPatient import Patient
from datetime import datetime

import pyreason as pr

import os
GCS_CONSTANT = 14
# INSULTS_CONSTANT = 0

class TriageLife(Triage):

    def __init__(self, thresholds):
        self.thresholds = thresholds


    def triage(self, patient: Patient) -> TriageScore:
        record = patient.physiology_record
        rationale_records = []
        score = 0.0


        if not record:
            return TriageScore(score=0.0, rationale=rationale_records, datetime_seconds=int(datetime.now().timestamp()),
                               algo_name="LifeTriage")





        # Reason at t=0
        interpretation = pr.reason(0, again=False)
        # pr.save_rule_trace(interpretation)
        next_time = interpretation.time + 1
        # next_time = 1


        edge_facts = []
        node_facts = []
        # Reason at t=1


        # gcs = 12
        # sbp = 85
        # rr = 28
        if not pd.isna(record['external_hemorrhage']):
            external_hemorrhage = record['external_hemorrhage']/10
            fact_add_e_h = pr.fact_edge.Fact(f'external_hemorrhage_f', ('personnel1', 'external_hemorrhage'),
                                             pr.label.Label('acs_value'), pr.interval.closed(external_hemorrhage, 1),
                                             next_time,
                                             next_time)
        else:
            fact_add_e_h = pr.fact_edge.Fact(f'external_hemorrhage_f', ('personnel1', 'external_hemorrhage'),
                                             pr.label.Label('acs_value'), pr.interval.closed(0,0),
                                             next_time,
                                             next_time)
        edge_facts.append(fact_add_e_h)

        if not pd.isna(record['tension_pneumothorax']):
            tension_pneumothorax = record['tension_pneumothorax']/10
            fact_add_t_p = pr.fact_edge.Fact(f'tension_pneumothorax_f', ('personnel1', 'tension_pneumothorax'),
                                             pr.label.Label('acs_value'), pr.interval.closed(tension_pneumothorax, 1),
                                             next_time,
                                             next_time)
        else:
            fact_add_t_p = pr.fact_edge.Fact(f'tension_pneumothorax_f', ('personnel1', 'tension_pneumothorax'),
                                             pr.label.Label('acs_value'), pr.interval.closed(0,0),
                                             next_time,
                                             next_time)
        edge_facts.append(fact_add_t_p)

        if not pd.isna(record['traumatic_brain_injury']):
            traumatic_brain_injury = record['traumatic_brain_injury']/10
            fact_add_t_b_i = pr.fact_edge.Fact(f'traumatic_brain_injury_f', ('personnel1', 'traumatic_brain_injury'),
                                               pr.label.Label('acs_value'),
                                               pr.interval.closed(traumatic_brain_injury, 1), next_time,
                                               next_time)
        else:
            fact_add_t_b_i = pr.fact_edge.Fact(f'traumatic_brain_injury_f', ('personnel1', 'traumatic_brain_injury'),
                                               pr.label.Label('acs_value'),
                                               pr.interval.closed(0,0), next_time,
                                               next_time)
        edge_facts.append(fact_add_t_b_i)

        if not pd.isna(record['gcs']):
            gcs = record['gcs']/1000
            fact_add_gcs = pr.fact_edge.Fact(f'gcs_f', ('personnel1', 'glasgow_coma_scale'), pr.label.Label('gcs_value'), pr.interval.closed(gcs, 1), next_time,
                                         next_time)
        else:
            fact_add_gcs = pr.fact_edge.Fact(f'gcs_f', ('personnel1', 'glasgow_coma_scale'),
                                             pr.label.Label('gcs_value'), pr.interval.closed(0,0), next_time,
                                             next_time)
        edge_facts.append(fact_add_gcs)

        if not pd.isna(record['sbp']):
            sbp = record['sbp'] / 1000
            fact_add_sbp = pr.fact_edge.Fact(f'sbp_f', ('personnel1', 'systolic_blood_pressure'), pr.label.Label('sbp_value'), pr.interval.closed(sbp, 1), next_time,
                                             next_time)
        else:
            fact_add_sbp = pr.fact_edge.Fact(f'sbp_f', ('personnel1', 'systolic_blood_pressure'),
                                             pr.label.Label('sbp_value'), pr.interval.closed(0,0), next_time,
                                             next_time)
        edge_facts.append(fact_add_sbp)

        if not pd.isna(record['rr']):
            rr = record['rr'] / 1000
            fact_add_rr = pr.fact_edge.Fact(f'rr_f', ('personnel1', 'respiration_rate'), pr.label.Label('rr_value'), pr.interval.closed(rr, 1), next_time,
                                             next_time)
        else:
            fact_add_rr = pr.fact_edge.Fact(f'rr_f', ('personnel1', 'respiration_rate'), pr.label.Label('rr_value'),
                                            pr.interval.closed(0,0), next_time,
                                            next_time)
        edge_facts.append(fact_add_rr)

        # curr_time = interpretation.time
        interpretation = pr.reason(again=True, edge_facts=edge_facts)
        next_time = interpretation.time + 1
        if not os.path.exists(f'traces_t{record["t"]}_1'):
            # Create the directory if it doesn't exist
            os.makedirs(f'traces_t{record["t"]}_1')
        pr.save_rule_trace(interpretation, f'traces_t{record["t"]}_1')


        # Check if gcs is missing
        df_gcs_missing = pr.filter_and_sort_nodes(interpretation, [('gcs_missing')])
        gcs_missing_flag = df_gcs_missing[2]['gcs_missing'][0]

        df_sbp_missing = pr.filter_and_sort_nodes(interpretation, [('sbp_missing')])
        sbp_missing_flag = df_sbp_missing[2]['sbp_missing'][0]

        df_rr_missing = pr.filter_and_sort_nodes(interpretation, [('rr_missing')])
        rr_missing_flag = df_rr_missing[2]['rr_missing'][0]


        if gcs_missing_flag == [1,1] and sbp_missing_flag != [1,1] and rr_missing_flag != [1,1]:
            estimate_gcs_flag = input('GCS value is missing. Do you want to enter estimated value for GCS? (y/n), if not then default (15) is used: ')
            if estimate_gcs_flag == 'y':
                estimated_gcs_value = int(input('Enter estimated value for GCS anywhere between 3 to 15: '))
            else:
                estimated_gcs_value = 15
            gcs = estimated_gcs_value / 1000
            fact_add_gcs = pr.fact_edge.Fact(f'gcs_f1', ('personnel1', 'glasgow_coma_scale'),
                                             pr.label.Label('gcs_value'), pr.interval.closed(gcs, 1), next_time,
                                             next_time)
            edge_facts.append(fact_add_gcs)
            interpretation = pr.reason(again=True, edge_facts=edge_facts)
            if not os.path.exists(f'traces_t{record["t"]}_2'):
                # Create the directory if it doesn't exist
                os.makedirs(f'traces_t{record["t"]}_2')
            pr.save_rule_trace(interpretation, f'traces_t{record["t"]}_2')

        elif sbp_missing_flag == [1,1] or rr_missing_flag == [1,1]:
            print('Vitals missing')
            simulate_vitals_flag = input('Vitals missing. Do you want to use DigitalTwin physiology data (y/n)? ')
            if simulate_vitals_flag == 'y':
                estimated_sbp_value = int(input('Enter simulation value for SBP value (1-219): '))
                estimated_rr_value = int(input('Enter simulation value for RR value (1-100): '))
                sbp = estimated_sbp_value / 1000
                rr = estimated_rr_value / 1000
                fact_add_sbp = pr.fact_edge.Fact(f'sbp_f1', ('personnel1', 'systolic_blood_pressure'),
                                                 pr.label.Label('sbp_value'), pr.interval.closed(sbp, 1), next_time,
                                                 next_time)
                fact_add_rr = pr.fact_edge.Fact(f'rr_f1', ('personnel1', 'respiration_rate'),
                                                pr.label.Label('rr_value'), pr.interval.closed(rr, 1), next_time,
                                                next_time)
                edge_facts.append(fact_add_sbp)
                edge_facts.append(fact_add_rr)
                interpretation = pr.reason(again=True, edge_facts=edge_facts)
                if not os.path.exists(f'traces_t{record["t"]}_2'):
                    # Create the directory if it doesn't exist
                    os.makedirs(f'traces_t{record["t"]}_2')
                pr.save_rule_trace(interpretation, f'traces_t{record["t"]}_2')
            else:
                print('RTS will not be computed')


        df_niss_flags = pr.filter_and_sort_nodes(interpretation, [('compute_niss')])
        df_niss_flag = False
        df_rts_flags = pr.filter_and_sort_nodes(interpretation, [('compute_rts')])
        df_rts_flag = False
        df_life_flags = pr.filter_and_sort_nodes(interpretation, [('compute_life')])
        df_life_flag = False

        for t, df in enumerate(df_niss_flags):
            if not df['compute_niss'].empty:
                if df['compute_niss'].iloc[0] == [1.0, 1.0]:
                    df_niss_flag = True
        for t, df in enumerate(df_rts_flags):
            if not df['compute_rts'].empty:
                if df['compute_rts'].iloc[0] == [1.0, 1.0]:
                    df_rts_flag = True
        for t, df in enumerate(df_life_flags):
            if not df['compute_life'].empty:
                if df['compute_life'].iloc[0] == [1.0, 1.0]:
                    df_life_flag = True
        if df_life_flag:
            print('LIFE score computed')
            algo_name = 'LIFE Triage Score'
            df_life_scores = pr.filter_and_sort_edges(interpretation, [('life_score')])
            for t, df in enumerate(df_life_scores):
                if not df['life_score'].empty:
                    life_score_normalized =df['life_score'].iloc[0][0]
                    life_score_denormalized = (life_score_normalized * (203.57 - 3.83)) + 3.83
                    score = life_score_denormalized

        elif not df_life_flag and not df_rts_flag and df_niss_flag:
            print('NISS score only')
            algo_name = 'NISS Triage Score'
            df_niss_scores = pr.filter_and_sort_edges(interpretation, [('niss_score')])
            for t, df in enumerate(df_niss_scores):
                if not df['niss_score'].empty:
                    niss_score_normalized = df['niss_score'].iloc[0][0]
                    niss_score_denormalized = (niss_score_normalized * (75 - 0)) + 0
                    score = niss_score_denormalized
        elif not df_life_flag and not df_niss_flag and df_rts_flag:
            print('RTS score only')
            algo_name = 'RTS Triage Score'
            df_rts_scores = pr.filter_and_sort_edges(interpretation, [('rts_score')])
            for t, df in enumerate(df_rts_scores):
                if not df['rts_score'].empty:
                    rts_score_normalized = df['rts_score'].iloc[0][0]
                    rts_score_denormalized = (rts_score_normalized * (75 - 0)) + 0
                    score = rts_score_denormalized
        else:
            algo_name = 'NO ALGORITHM'
            print('NO score')


        x=1
        # for vital_name, threshold in self.thresholds.items():
            # if vital_name in record:
            #     value = record[vital_name]
            #
            #     print(f"Record {record}")
            #     print(f"vital_name {vital_name}")
            #     print(f"value {value}")
            #     print(f"threshold {threshold}")
            #     print(f"score {score}")
            #
            #
            #     rationale_records.append(RationaleRecord(vital=Vital(name=vital_name, value=value), score=value,
            #                                              threshold=threshold.max_value))




        # Return the TriageScore with the total score, rationale, datetime, and algorithm name
        # class TriageScore(BaseModel):
        #     datetime_seconds: int
        #     algo_name: str
        #     score: float
        #     confidence: float
        #     rationale: List[RationaleRecord]
        #     interaction: Optional[Interaction]
        #
        return TriageScore(
            datetime_seconds=int(datetime.now().timestamp()),
            algo_name=algo_name,
            score=score,
            confidence=1,
            rationale=rationale_records,
            interaction = None
        )
