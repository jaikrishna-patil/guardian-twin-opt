

from services.service_optimization.factory.FactoryAlgo import AlgoName, FactoryAlgos
from services.models.ModelConstraints import Constraint
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets
from services.models.ModelAsset import Asset
from services.models.ModelCareFacility import CareFacility
import json
import random
import time
import tracemalloc
import pandas as pd
import argparse
import os
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import plotly.graph_objects as go
import plotly.io as pio

# Set the font and style to match the paper
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 14
rcParams['xtick.labelsize'] = 10
rcParams['ytick.labelsize'] = 10
rcParams['legend.fontsize'] = 10
rcParams['lines.linewidth'] = 1.5
rcParams['axes.linewidth'] = 0.8
rcParams['axes.labelweight'] = 'bold'  # Bold axis labels

def create_sankey(casualties, statuses, values, title, filename):
    labels = casualties + ['Served', 'Not Served']
    sources = list(range(len(casualties)))
    targets = [len(casualties) + (0 if status == 'Served' else 1) for status in statuses]

    # Assign colors to the links
    # link_colors = [colors[i % len(colors)] for i in range(len(values))]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=sources,  # Indices correspond to `labels`
            target=targets,
            value=values
            # color=link_colors  # Apply colors to the links
        )
    ))

    fig.update_layout(title_text=title, font_size=10)

    # Save the plot as a PNG file
    pio.write_image(fig, filename)
    print(f"Saved {filename}")
def plot_sankey(assignment, all_cas, person_score, person_rtd, person_equipments, req_ts):
    print(all_cas)
    status = []

    # Weights for each triage type (normalized to thin the lines)
    triage_score = []  # scaled down
    rtd_ts = []  # scaled down
    equipments_needed = []  # scaled down
    req_cas = []
    for key, value in req_ts.items():
        person,_,_ = key
        req_cas.append(person)

    remove_cas = set(all_cas).difference(set(req_cas))
    all_cas = list(set(all_cas).difference(set(remove_cas)))
    print(all_cas)


    for cas in all_cas:
        if cas in assignment.keys():
            status.append('Served')
        else:
            status.append('Not Served')
        triage_score.append(person_score[cas]*100)
        rtd_ts.append(person_rtd[cas]*100)
        equipments_needed.append(person_equipments[cas]*100)
    print(person_score)
    print(person_rtd)
    print(person_equipments)
    create_sankey(casualties=all_cas, statuses=status, values=triage_score, title=f'score', filename='figs/plot_sankey_score.png')
    create_sankey(casualties=all_cas, statuses=status, values=rtd_ts, title=f'rtd',
                  filename='figs/plot_sankey_rtd.png')
    create_sankey(casualties=all_cas, statuses=status, values=equipments_needed, title=f'equi',
                  filename='figs/plot_sankey_equi.png')
def plot_radar_chart(data, accepted):
    # Input values
    criteria = ['Primary', 'Reverse', 'Situational']

    # Normalize the data
    max_values = data['Theoretical best']
    normalized_data = {}
    for label, d in data.items():
        normalized_data[label] = [d[i] / max_values[i] for i in range(len(d))]

    # Number of variables we're plotting.
    num_vars = len(criteria)

    # Split the circle into even parts and save the angles
    # so we know where to put each axis.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The radar chart is a circle, so we need to "complete the loop"
    # and append the start value to the end.
    angles += angles[:1]

    # Create the figure and the polar subplot.
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))  # Increase figure size

    del normalized_data['Theoretical best']
    # Plot each individual data set with different line styles.
    line_styles = {'Primary solution': 'solid', 'Reverse solution': '--', 'Situational solution': 'dotted'}

    for label, d in normalized_data.items():
        values = d + d[:1]
        ax.plot(angles, values, label=label, linestyle=line_styles[label])
        ax.fill(angles, values, alpha=0.25)

    # Set y-ticks to create 20 equally spaced circles
    num_circles = 10
    ax.set_yticks([i / num_circles for i in range(num_circles + 1)])
    ax.set_yticklabels([f'{int(10 * i)}%' for i in range(num_circles + 1)])

    # Labels for each point.
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria, va='center', ha='left')

    # Ensure the outermost circle represents the maximum value for each axis
    ax.set_ylim(0, 1)

    # Title and legend.
    # plt.title(f'Chosen solution: {accepted}', size=20, weight='bold', color='black', y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.05))  # Adjust legend position

    plt.tight_layout()  # Automatically adjust subplot parameters for padding

    # Save the figure
    plt.savefig('radar_chart_paper_style.png', dpi=300, bbox_inches='tight')  # Save as PNG with high resolution

    plt.show()
def main(n_casualties, n_assets, n_cfs):


    # cas_indexes = random.sample(range(1, 501), n_casualties)
    # assets_indexes = random.sample(range(1, 501), n_assets)
    # cfs_indexes = random.sample(range(1, 101), n_cfs)
    # # Save the indices to a CSV file
    # filename = 'indices.csv'
    #
    # with open(filename, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['casualty_index', 'asset_index', 'cf_index'])
    #
    #     # Write the indices
    #     for i in range(max(len(cas_indexes), len(assets_indexes), len(cfs_indexes))):
    #         casualty = cas_indexes[i] if i < len(cas_indexes) else ''
    #         asset = assets_indexes[i] if i < len(assets_indexes) else ''
    #         cf = cfs_indexes[i] if i < len(cfs_indexes) else ''
    #         writer.writerow([casualty, asset, cf])
    #
    # print(f"Indices saved to {filename}")

    # Read the indices back from the CSV file and ensure they are integers
    df_indices = pd.read_csv("indices.csv")
    cas_indexes = list(df_indices["casualty_index"].dropna().astype(int))
    assets_indexes = list(df_indices["asset_index"].dropna().astype(int))
    cfs_indexes = list(df_indices["cf_index"].dropna().astype(int))

    assets_possible = []
    cfs_possible = []
    all_mission_options = []
    all_assets = []
    all_care_facilities = []

    print('Assets')
    for i in assets_indexes:
        folder_p = 'data/asset_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        all_assets.append(
            Asset(asset_name=data['name'], crew_duty_hrs=data['crew_duty_hrs'], asset_range_in_km=data['range_km'],
                  asset_speed_kmph=data['speed_kph'], location=[data['latitude'], data['longitude']]))
        assets_possible.append(data['name'])
    print('Care facilties')
    for i in cfs_indexes:
        folder_p = 'data/cf_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        all_care_facilities.append(CareFacility(cf_name=data['name'], location=[data['latitude'], data['longitude']]))
        cfs_possible.append(data['name'])
    print('Casualties')
    for i in cas_indexes:
        folder_p = 'data/casualty_dataset'
        file_path = f'{folder_p}/{i}.json'
        # Open and read the JSON file
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # print(data)
        insults = [key for key in data.keys() if key.startswith('insult')]
        insults_dict = {key: val for key, val in data.items() if key in insults}
        vitals_dict = {
            'gcs': data['gcs'],
            'sbp': data['sbp'],
            'rr': data['rr']
        }
        all_mission_options.append(
            MissionOptionsAssets(patient_name=data['name'], care_facilities_possible=cfs_possible,
                                 assets_possible=assets_possible, insults_dict=insults_dict, vitals_dict=vitals_dict,
                                 location=[data['latitude'], data['longitude']]))

    # print("")
    # print("ALGO :: Mission options assets -> Mission final asset")
    algo_mission_assets = FactoryAlgos.create_algo(mode= AlgoName.MULTIPLE_OBJ)
    start = time.time()
    tracemalloc.start()
    (mission_final_assets, accepted, assignment_final, (assignment_primary, assignment_reverse, assignment_situational),
     all_persons, person_scores, person_lsi_ts, person_rtd_ts, person_equipments_needed, req_ts,
     (primary_sol_primary_obj, reverse_sol_primary_obj, situational_sol_primary_obj),
     (primary_sol_reverse_obj, reverse_sol_reverse_obj, situational_sol_reverse_obj),
     (primary_sol_situational_obj, reverse_sol_situational_obj, situational_sol_situational_obj)) = algo_mission_assets.return_final_assignments_multiple_obj(missions_options=all_mission_options, assets=all_assets, care_facilities=all_care_facilities,
                                                                                                                                                              objectives = ['PRIMARY', 'REVERSE', 'SITUATIONAL'])
    t = round(time.time() - start, 3)
    mem = round(tracemalloc.get_traced_memory()[1] / (10 ** 6), 3)
    tracemalloc.stop()
    print('TIME:', t)
    print('MEMORY:', mem)
    if accepted == 'None':
        solution_found = 0
    else:
        solution_found = 1
    num_casualties_served = len(assignment_final.keys())
    print((primary_sol_primary_obj, reverse_sol_primary_obj, situational_sol_primary_obj),
     (primary_sol_reverse_obj, reverse_sol_reverse_obj, situational_sol_reverse_obj),
     (primary_sol_situational_obj, reverse_sol_situational_obj, situational_sol_situational_obj))
    # data = {
    #     'Theoretical best': [primary_sol_primary_obj, reverse_sol_reverse_obj, primary_sol_primary_obj],
    #     'Primary solution': [primary_sol_primary_obj, primary_sol_reverse_obj, primary_sol_situational_obj],
    #     'Reverse solution': [reverse_sol_primary_obj, reverse_sol_reverse_obj, reverse_sol_situational_obj],
    #     'Situational solution': [situational_sol_primary_obj, situational_sol_reverse_obj,
    #                              situational_sol_situational_obj]
    # }
    # plot_radar_chart(data=data, accepted=accepted)
    # plot_sankey(assignment=assignment_final, all_cas=all_persons, person_score=person_scores, person_rtd=person_rtd_ts,
    #             person_equipments=person_equipments_needed, req_ts=req_ts)

    # Plot radar chart
    # if solution_found==1:
    #     # Plot
    #     data = {
    #         'Theoretical best': [primary_sol_primary_obj, reverse_sol_reverse_obj, situational_sol_situational_obj],
    #         'Primary solution': [primary_sol_primary_obj, primary_sol_reverse_obj, primary_sol_situational_obj],
    #         'Reverse solution': [reverse_sol_primary_obj, reverse_sol_reverse_obj, reverse_sol_situational_obj],
    #         'Situational solution': [situational_sol_primary_obj, situational_sol_reverse_obj, situational_sol_situational_obj]
    #     }
    #     plot_radar_chart(data=data, accepted=accepted)
    #     plot_sankey(assignment=assignment_final, all_cas=all_persons, person_score=person_scores, person_rtd=person_rtd_ts, person_equipments=person_equipments_needed, req_ts = req_ts)




    # Create a DataFrame with the required data
    df = pd.DataFrame({
        'num_cas': [n_casualties],
        'num_assets': [n_assets],
        'time': [t],
        'memory': [mem],
        'solution_found': [solution_found],
        'num_cas_served': [num_casualties_served],
        'accepted_triage': [accepted],
        'primary_sol_primary_obj': [primary_sol_primary_obj],
        'reverse_sol_primary_obj': [reverse_sol_primary_obj],
        'situational_sol_primary_obj': [situational_sol_primary_obj],
        'primary_sol_reverse_obj': [primary_sol_reverse_obj],
        'reverse_sol_reverse_obj': [reverse_sol_reverse_obj],
        'situational_sol_reverse_obj': [situational_sol_reverse_obj],
        'primary_sol_situational_obj': [primary_sol_situational_obj],
        'reverse_sol_situational_obj': [reverse_sol_situational_obj],
        'situational_sol_situational_obj': [situational_sol_situational_obj]


    })

    # Define the CSV file path
    csv_file_path = 'baseline_multiple_tables/experiment_objective_values.csv'

    # Append the DataFrame to the CSV file
    if not os.path.isfile(csv_file_path):
        df.to_csv(csv_file_path, index=False)
    else:
        df.to_csv(csv_file_path, mode='a', header=False, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--n_casualties', type=int, default=10, help='number of casualties')
    parser.add_argument('--n_assets', type=int, default=5, help='number of assets')
    parser.add_argument('--n_cfs', type=int, default=1, help='number of care facilities')

    args = parser.parse_args()
    main(args.n_casualties, args.n_assets, args.n_cfs)