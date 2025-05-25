from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Optional, Any
class Constraint(BaseModel):
    """
        A Pydantic model representing a constraint for medical evacuation (MEDEVAC) planning.

        This class defines a constraint that can be applied in the MEDEVAC planning process,
        such as Life-Saving Intervention (LSI) or air time limitations.

        Attributes:
            constraint_name (str): The name of the constraint. Must be either 'lsi' or 'air_time'.
            constraint_threshold (Optional[float]): An optional threshold value for the constraint.
                eg: optionally used for the 'air_time' constraint to specify maximum air time allowed non-stop.

        Methods:
            validate_constraint_name: A field validator to ensure that the constraint_name
                is one of the allowed values.

        Raises:
            ValueError: If an invalid constraint_name is provided.

        Example:
            lsi_constraint = Constraint(constraint_name='lsi')
            air_time_constraint = Constraint(constraint_name='air_time', constraint_threshold=3.0)
        """

    constraint_name: str
    constraint_threshold: Optional[float] = None

    # Custom validator to ensure constraint_name is one of the allowed values
    @field_validator('constraint_name')
    def validate_constraint_name(cls, v):
        """
                Validate the constraint_name field.

                Args:
                    v (str): The constraint name to validate.

                Returns:
                    str: The validated constraint name.

                Raises:
                    ValueError: If the constraint name is not one of the allowed values.
                """
        allowed_names = {'lsi', 'air_time'}
        if v not in allowed_names:
            raise ValueError(f"constraint_name must be one of {allowed_names}")
        return v
