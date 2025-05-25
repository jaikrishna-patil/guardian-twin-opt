import networkx as nx

# ================================ CREATE GRAPH====================================
# Create a Directed graph
g = nx.DiGraph()

#Add personnels : Can add more
g.add_node('personnel1', personnel_id=2, type_personnel='1,1', first_name='John', last_name='Doe', rank='sergeant', call_sign='maverick', gender='male', age=30, weight_lb=176, height_cm=170, blood_type='B+',
           gcs_missing='0,1', sbp_missing='0,1', rr_missing='0,1', external_hemorrhage_missing='0,1', tension_pneumothorax_missing='0,1', traumatic_brain_injury_missing='0,1', compute_niss='0,0', compute_rts='0,0', compute_life='0,0')

# Add insults:
g.add_node('external_hemorrhage', insult_id=2, type_external_hemorrhage='1,1', insult_label='external_hemorrhage', insult_category='hemorrhage', body_location='arm', body_sublocation='lower', lateral_position='left')
g.add_node('tension_pneumothorax', insult_id=3, type_tension_pneumothorax='1,1', insult_label='tension_pneumothorax', abbreviation='TPTX', insult_category='respiratory', body_location='chest', body_sublocation='lung', lateral_position='left')
g.add_node('traumatic_brain_injury', insult_id=4, type_traumatic_brain_injury='1,1', insult_label='traumatic_brain_injury', abbreviation='TBI', insult_category='nervous_system', body_location='head', body_sublocation='brain', lateral_position='left')

#Add vitals

g.add_node('heart_rate', vital_id=2, type_vital_heart_rate='1,1', vital_label='heart_rate', abbreviation='HR')
g.add_node('systolic_blood_pressure', type_vital_systolic_blood_pressure='1,1', vital_id=3, vital_label='systolic_blood_pressure', abbreviation='sys-bp')
g.add_node('diastolic_blood_pressure', type_vital_diastolic_blood_pressure='1,1', vital_id=4, vital_label='diastolic_blood_pressure', abbreviation='dia-bp')
g.add_node('mean_arterial_pressure', type_vital_mean_arterial_pressure='1,1', vital_id=5, vital_label='mean_arterial_pressure', abbreviation='map')
g.add_node('respiration_rate', vital_id=6, type_vital_respiration_rate='1,1', vital_label='respiration_rate', abbreviation='rr')
g.add_node('oxygen_saturation', vital_id=7, type_vital_oxygen_saturation='1,1', vital_label='oxygen_saturation', abbreviation='spo2')
g.add_node('end_tidal_co2', vital_id=8, type_vital_end_tidal_co2='1,1', vital_label='end_tidal_co2', abbreviation='etco2')
g.add_node('temperature', vital_id=9, type_vital_temperature='1,1', vital_label='temperature', abbreviation='temp')
g.add_node('urinary_output_per_hr', vital_id=10, type_vital_urinary_output_per_hr='1,1',  vital_label='urinary_output_per_hr', abbreviation='uo/hr')
g.add_node('urinary_output_per_day', vital_id=11, type_vital_urinary_output_per_day='1,1', vital_label='urinary_output_per_day', abbreviation='uo/day')

#Add scales
g.add_node('glasgow_coma_scale', scale_id=2, type_gcs='1,1', scale_label='glasgow_coma_scale', abbreviation='gcs')

#Add triages
g.add_node('niss', triage_id=2, type_niss='1,1', triage_label='niss')
g.add_node('rts', triage_id=3, type_rts='1,1', triage_label='rts')
g.add_node('life', triage_id=4, type_life='1,1', triage_label='life')




#Add edges <personnel, vital>
g.add_edge('personnel1', 'heart_rate', hr_value='0,1')
g.add_edge('personnel1', 'systolic_blood_pressure', sbp_value='0,1')
g.add_edge('personnel1', 'diastolic_blood_pressure', vital_value='0,1')
g.add_edge('personnel1', 'mean_arterial_pressure', vital_value='0,1')
g.add_edge('personnel1', 'respiration_rate', rr_value='0,1')
g.add_edge('personnel1', 'oxygen_saturation', vital_value='0,1')
g.add_edge('personnel1', 'end_tidal_co2', vital_value='0,1')
g.add_edge('personnel1', 'temperature', vital_value='0,1')
g.add_edge('personnel1', 'urinary_output_per_hr', vital_value='0,1')
g.add_edge('personnel1', 'urinary_output_per_day', vital_value='0,1')




#add edges <personnel, insult>
g.add_edge('personnel1', 'external_hemorrhage', acs_value='0,1', acs_available='1,1')
g.add_edge('personnel1', 'tension_pneumothorax', acs_value='0,1', acs_available='1,1')
g.add_edge('personnel1', 'traumatic_brain_injury', acs_value='0,1', acs_available='1,1')

#add edges <personnel, scale>
# g.add_edge('personnel1', 'glasgow_coma_scale', gcs_3='0,1', gcs_4='0,1', gcs_5='0,1', gcs_6='0,1', gcs_7='0,1', gcs_8='0,1', gcs_9='0,1', gcs_10='0,1', gcs_11='0,1', gcs_12='0,1', gcs_13='0,1', gcs_14='0,1', gcs_15='0,1')
g.add_edge('personnel1', 'glasgow_coma_scale', gcs_value='0,1')

#Add edges <personnel, triage>
g.add_edge('personnel1', 'niss', niss_score='0,1')
g.add_edge('personnel1', 'rts', rts_score='0,1')
g.add_edge('personnel1', 'life', life_score='0,1')

nx.write_graphml_lxml(g, f'john_doe.graphml', named_key_ids=True)
