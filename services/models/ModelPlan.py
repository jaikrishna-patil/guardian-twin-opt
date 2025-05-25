
from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Optional, Any



class Plan(BaseModel):
    """
        A Pydantic model representing a medical evacuation (MEDEVAC) plan.

        This class defines the structure for storing urgency-based and reverse triage-based
        evacuation plans. Each plan is represented as a list of dictionaries, where each
        dictionary contains the assignment details for a casualty.

        Attributes:
            urgency_plan (List[Optional[dict]]): A list of dictionaries representing
                the urgency-based evacuation plan. Each dictionary contains assignment
                details for a casualty based on urgency triage. Defaults to an empty list.

            reverse_plan (List[Optional[dict]]): A list of dictionaries representing
                the reverse triage-based evacuation plan. Each dictionary contains
                assignment details for a casualty based on reverse triage. Defaults to an empty list.

        Example:
            plan = Plan(
                urgency_plan=[
                    {"casualty1": ("asset1", "hospital1", 2.5)},
                    {"casualty2": ("asset2", "hospital2", 1.8)}
                ],
                reverse_plan=[
                    {"casualty1": ("asset2", "hospital1", 3.2)},
                    {"casualty2": ("asset4", "hospital4", 2.1)}
                ]
            )

        Note:
            The dictionaries in each plan typically follow the structure:
            {casualty_name: (assigned_asset, assigned_hospital, evacuation_time_hrs)}
            """
    urgency_plan: List[Optional[dict]] = []
    reverse_plan: List[Optional[dict]] = []

