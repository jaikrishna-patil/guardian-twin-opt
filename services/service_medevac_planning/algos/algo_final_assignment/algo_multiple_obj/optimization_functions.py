import pyreason as pr
import os

from mip import Model, xsum, maximize, BINARY, OptimizationStatus



def use_milp_reverse_triage(persons, assets, hospitals, required_timesteps, required_timesteps_lsi_only, rtd_timesteps, person_lsi_ts, required_ts_asset_isop, required_ts_isop_cf, constraint_lsi=False, constraint_air_time=False, threshold_air_time=1):
    """
        Perform reverse triage optimization using Mixed Integer Linear Programming (MILP).

        This function optimizes the assignment of persons to assets and hospitals based on various constraints
        and objectives, prioritizing the rescue of individuals with less return time to duty.

        Args:
            persons (list): List of persons to be triaged.
            assets (list): List of available assets for rescue operations.
            hospitals (list): List of available hospitals.
            required_timesteps (dict): Dictionary of required timesteps for each (person, asset, hospital) combination.
            required_timesteps_lsi_only (dict): Dictionary of required timesteps for getting lsi to casualty.
            rtd_timesteps (dict): Dictionary of remaining time to duty for each person.
            person_lsi_ts (dict): Dictionary of maximum timesteps for each person to get lsi and save its life.
            required_ts_asset_isop (dict): Dictionary of required timesteps from asset to ISOP for each combination.
            required_ts_isop_cf (dict): Dictionary of required timesteps from ISOP to care facility for each combination.
            constraint_lsi (bool): Whether to apply LSI constraints. Default is False.
            constraint_air_time (bool): Whether to apply air time constraints. Default is False.
            threshold_air_time (int): Threshold for air time constraints. Default is 1.

        Returns:
            tuple: A tuple containing:
                - assignment (dict): Optimal assignment of persons to assets and hospitals.
                - obj_value (float): Optimal objective value.
                - Z (dict): Decision variables for assignments.
                - Y (dict): Decision variables for person selection.
        """
    # Create a new model
    m = Model()

    # Decision variables
    Z = {}
    for (p, r, h), _ in required_timesteps.items():
        Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

    Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

    m.objective = maximize(xsum(
        100*Y[p] + Y[p] * (1 / (1 + rtd_timesteps[p])) for p in persons) - 0.1 * xsum(
        required_timesteps[(p, r, h)] * Z[r, p, h] for p in persons for r in assets
        for h in hospitals if (p, r, h) in required_timesteps))

    # Constraints
    # Each person can be served by only one asset and transported to one hospital
    for p in persons:
        m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

    # Each asset can serve at most one person at a time
    for r in assets:
        m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1

    # New constraint: A casualty can only be assigned an asset and hospital if the required_timestep <= lsi_ts[p]
    if constraint_lsi:
        for p in persons:
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps_lsi_only:
                        m += Z[r, p, h] * required_timesteps_lsi_only[(p, r, h)] <= person_lsi_ts[p]
    if constraint_air_time:
        for p in persons:
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps_lsi_only:
                        m += Z[r, p, h] * required_ts_asset_isop[(p, r, h)] <= threshold_air_time
                        m += Z[r, p, h] * required_ts_isop_cf[(p, r, h)] <= threshold_air_time
    # Optimize the model
    status = m.optimize()
    # Check if a solution was found
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print("Solution found:")
    elif status == OptimizationStatus.INFEASIBLE:
        print("No feasible solution found.")
    elif status == OptimizationStatus.UNBOUNDED:
        print("The problem is unbounded.")
    else:
        print("Optimization status:", status)

    # Extract the solution
    assignment = {}
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        for r in assets:
            for p in persons:
                for h in hospitals:
                    if (p, r, h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                        assignment[p] = (r, h, required_timesteps[(p, r, h)])

    obj_value = None
    if m.num_solutions>0:
        print(f"Optimal objective value: {m.objective_value}")
        obj_value = m.objective_value

    return assignment, obj_value, Z, Y

def use_milp_urgency_triage(persons, assets, hospitals, required_timesteps, required_timesteps_lsi_only,
                                person_score, person_lsi_ts, required_ts_asset_isop, required_ts_isop_cf,
                                constraint_lsi=False, constraint_air_time=False, threshold_air_time=1):
    """
            Perform urgency based/ triage score based optimization using Mixed Integer Linear Programming (MILP).

            This function optimizes the assignment of persons to assets and hospitals based on various constraints
            and objectives, prioritizing the rescue of individuals with higher normalized triage scores.

            Args:
                persons (list): List of persons to be triaged.
                assets (list): List of available assets for rescue operations.
                hospitals (list): List of available hospitals.
                required_timesteps (dict): Dictionary of required timesteps for each (person, asset, hospital) combination.
                required_timesteps_lsi_only (dict): Dictionary of required timesteps for getting lsi to casualty.
                person_score (dict): Dictionary of normalized triage scores for each person.
                person_lsi_ts (dict): Dictionary of maximum timesteps for each person to get lsi and save its life.
                required_ts_asset_isop (dict): Dictionary of required timesteps from asset to ISOP for each combination.
                required_ts_isop_cf (dict): Dictionary of required timesteps from ISOP to care facility for each combination.
                constraint_lsi (bool): Whether to apply LSI constraints. Default is False.
                constraint_air_time (bool): Whether to apply air time constraints. Default is False.
                threshold_air_time (int): Threshold for air time constraints. Default is 1.

            Returns:
                tuple: A tuple containing:
                    - assignment (dict): Optimal assignment of persons to assets and hospitals.
                    - obj_value (float): Optimal objective value.
                    - Z (dict): Decision variables for assignments.
                    - Y (dict): Decision variables for person selection.
            """
    # Create a new model
    m = Model()

    # Decision variables
    Z = {}
    for (p, r, h), _ in required_timesteps.items():
        Z[r, p, h] = m.add_var(name=f"Z({r},{p},{h})", var_type=BINARY)

    Y = {p: m.add_var(name=f"Y({p})", var_type=BINARY) for p in persons}

    m.objective = maximize(xsum(
        100*Y[p] + 100*Y[p] * person_score[p] for p in persons) - 0.1 * xsum(
        required_timesteps[(p, r, h)] * Z[r, p, h] for p in persons for r in assets
        for h in hospitals if (p, r, h) in required_timesteps))

    # Constraints
    # Each person can be served by only one asset and transported to one hospital
    for p in persons:
        m += xsum(Z[r, p, h] for r in assets for h in hospitals if (p, r, h) in required_timesteps) >= Y[p]

    # Each asset can serve at most one person at a time
    for r in assets:
        m += xsum(Z[r, p, h] for p in persons for h in hospitals if (p, r, h) in required_timesteps) <= 1
    # New constraint: A casualty can only be assigned an asset and hospital if the required_timestep <= lsi_ts[p]
    if constraint_lsi:
        for p in persons:
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps_lsi_only:
                        m += Z[r, p, h] * required_timesteps_lsi_only[(p, r, h)] <= person_lsi_ts[p]
    if constraint_air_time:
        for p in persons:
            for r in assets:
                for h in hospitals:
                    if (p, r, h) in required_timesteps_lsi_only:
                        m += Z[r, p, h] * required_ts_asset_isop[(p, r, h)] <= threshold_air_time
                        m += Z[r, p, h] * required_ts_isop_cf[(p, r, h)] <= threshold_air_time
    # Optimize the model
    status = m.optimize()
    # Check if a solution was found
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print("Solution found:")
    elif status == OptimizationStatus.INFEASIBLE:
        print("No feasible solution found.")
    elif status == OptimizationStatus.UNBOUNDED:
        print("The problem is unbounded.")
    else:
        print("Optimization status:", status)

    # Extract the solution
    assignment = {}
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        for r in assets:
            for p in persons:
                for h in hospitals:
                    if (p, r, h) in required_timesteps and Z[r, p, h].x > 0:  # Adjust the threshold as needed
                        assignment[p] = (r, h, required_timesteps[(p, r, h)])
    obj_value = None
    if m.num_solutions>0:
        print(f"Optimal objective value: {m.objective_value}")
        obj_value = m.objective_value

    return assignment, obj_value, Z, Y