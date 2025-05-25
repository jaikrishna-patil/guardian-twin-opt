class CareFacility:
    """
    Initial implementation any values to be passed in as a specifications_record.
    Very likely we will want to strongly type this in the future.  For now, have assumed a level of flexibility
    """
    def __init__(self, **specifications_record):
        self.specifications_record = specifications_record