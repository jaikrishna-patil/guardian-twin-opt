
from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Optional, Any

from services.models.ModelConstraints import Constraint


class Settings(BaseModel):
    """
        A Pydantic model representing the settings for medical evacuation (MEDEVAC) planning.

        This class defines the configuration options for triage algorithms, optimization types,
        and constraints to be applied in the MEDEVAC planning process.

        Attributes:
            enabled_triage_algos (list): A list of enabled triage algorithms.
                Allowed values are 'life', 'rts', and 'niss'.
            enabled_urgency_opt (bool): Flag to enable urgency-based optimization.
                Defaults to False.
            enabled_reverse_opt (bool): Flag to enable reverse triage optimization.
                Defaults to False.
            constraints (List[Constraint]): A list of Constraint objects representing
                the constraints to be applied in the optimization process.

        Methods:
            validate_triage_algos: A field validator to ensure that only allowed
                triage algorithm values are used.

        Raises:
            ValueError: If an invalid triage algorithm is provided in enabled_triage_algos.

        Example:
            settings = Settings(
                enabled_triage_algos=['life', 'rts'],
                enabled_urgency_opt=True,
                enabled_reverse_opt=False,
                constraints=[Constraint(constraint_name='lsi')]
            )
        """
    enabled_triage_algos: list = []

    enabled_urgency_opt: bool = False
    enabled_reverse_opt: bool = False

    constraints: List[Constraint] = []

    # Define a custom validator for the 'enabled_triage_algos' field
    @field_validator('enabled_triage_algos')
    def validate_triage_algos(cls, v):
        """
                Validate the enabled_triage_algos field.

                Args:
                    v (list): The list of triage algorithms to validate.

                Returns:
                    list: The validated list of triage algorithms.

                Raises:
                    ValueError: If any algorithm in the list is not one of 'life', 'rts', or 'niss'.
                """
        allowed_values = {'life', 'rts', 'niss'}
        if any(algo not in allowed_values for algo in v):
            raise ValueError(f"enabled_triage_algos can only contain values from {allowed_values}")
        return v
