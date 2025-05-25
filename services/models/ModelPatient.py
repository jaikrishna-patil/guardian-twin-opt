class Patient:
    """
    Initial implementation any values to be passed in as a physiology_record.
    Very likely we will want to strongly type this in the future.  For now, have assumed a level of flexibility
    """
    def __init__(self, **physiology_record):
        self.physiology_record = physiology_record