from mip import Model, xsum, maximize, BINARY
def solve_patient_resource_allocation_ip(patients, patients_scores, patient_requirements, resources, resource_availability):
    # Create a MIP model
    model = Model()

    # Decision variables: x_i is 1 if patient i is fully served, 0 otherwise
    x = {p: model.add_var(var_type=BINARY, name=f"x({p})") for p in patients}

    # Objective: Maximize the total score of served patients
    model.objective = maximize(xsum(patients_scores[p] * x[p] for p in patients))

    # Constraints: Ensure resource availability is respected
    for r in resources:
        model += xsum(patient_requirements[p].get(r, 0) * x[p] for p in patients) <= resource_availability[r], f"Resource_{r}_constraint"

    # Solve the model
    model.optimize()

    # Extract the results: list of patients that are served
    served_patients = [p for p in patients if x[p].x >= 0.99]

    return served_patients