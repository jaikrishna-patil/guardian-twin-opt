import os
import sys
from flask import Blueprint, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from gt_service_tools.utils.medical.burn_injuries import (
    GroupBurnsByLocation,
    GetBurnTBSA,
    GetBurnAISSeverity
)
api_bp = Blueprint('burn_api', __name__)

@api_bp.route('/api/get_burn_tbsa', methods=['POST'])
def get_tbsa():
    burn_tbsa_data = request.json
    tbsa_algorithm = burn_tbsa_data.get('algorithm', 'rule_of_nines')
    get_burn_tbsa = GetBurnTBSA()
    try:
        tbsa = get_burn_tbsa.get_tbsa_from_location(burn_tbsa_data, tbsa_algorithm)
        return jsonify({"tbsa": tbsa})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/api/get_burn_AIS_severity', methods=['POST'])
def get_ais_severity():
    burn_injury_group = request.json
    get_burn_ais_severity = GetBurnAISSeverity()
    try:
        ais_severity_score = get_burn_ais_severity.get_ais_severity_score(burn_injury_group)
        return jsonify({"AIS_severity_score": ais_severity_score})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/api/get_location_group_for_burn', methods=['POST'])
def get_location_group_for_burn():
    burn_injury = request.json
    group_burn_by_location = GroupBurnsByLocation()
    try:
        location_group = group_burn_by_location.get_location_group_for_burn(burn_injury)
        return jsonify(location_group)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

 
# @api_bp.route('/api/group_burn_injuries_by_degree', methods=['POST'])
# def group_burn_injuries_by_degree():
#     print('api group_burn_injuries_by_degree')
#     print(f"request.json: {request.json}")
#     patient_injuries = request.json.get('patient_injuries', [])
#     group_burn_injuries = GroupBurnInjuriesByDegree()
#     try:
#         body_part_group = group_burn_injuries.get_body_part_group(patient_injuries)
#         return jsonify(body_part_group)
#     except ValueError as e:
#         print(f"ValueError: {e}")
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         print(f"Exception: {e}")
#         return jsonify({"error": "An unexpected error occurred."}), 500

# @api_bp.route('/api/group_burn_injuries_by_degree', methods=['POST'])
# def group_burn_injuries_by_degree():
#     data = request.json
#     scenario = data.get('scenario')
#     group_burn_injuries = GroupBurnInjuriesByDegree()
#     group_burn_injuries.get_all_patient_states(scenario)
#     group_burn_injuries.get_patient_burn_injuries()
#     grouped_burn_injuries = group_burn_injuries.get_body_part_group()
#     return jsonify(grouped_burn_injuries)