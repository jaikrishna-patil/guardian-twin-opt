class MissionRequirements:
    """
    Initial implementation any values to be passed in as a mission_requirements_record.
    Very likely we will want to strongly type this in the future.  For now, have assumed a level of flexibility
    """
    def __init__(self, **mission_requirements_record):
        self.mission_requirements_record = mission_requirements_record