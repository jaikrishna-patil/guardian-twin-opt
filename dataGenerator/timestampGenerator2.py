from datetime import datetime, timedelta
import random
import ast
from randomizer import Random
from utils import Utils
from setRangeGenerator import SetRangeGenerator
from collections import OrderedDict
# from dataProcessor import Process


# TIMESTAMP_KEY = '_generate_timestamps'
class TimestampGenerator2:
    def __init__(self, process_instance, Utils):
        self.process_instance = process_instance
        self.Utils = Utils
        self.counters = {}
        already_selected = []

    def generate_timestamp(self, generated_item=None, timestamp_meta=None, last_timestamp=None):
        # Ensure generated_item is a dictionary
        if generated_item is None:
            generated_item = {}
        elif not isinstance(generated_item, dict):
            print(f"generated item:{generated_item}")
            raise TypeError(f"Expected generated_item to be a dict, got {type(generated_item).__name__}")

        # delta is the randomly generated difference between each timestamp
        min_delta, max_delta = self._get_time_deltas(timestamp_meta)
        delta_minutes = random.randint(min_delta, max_delta)

        # Initialize the starting datetime
        timestamp = self._set_start_datetime(timestamp_meta)

        # If last_timestamp is provided, add the delta to the last timestamp
        if last_timestamp:
            timestamp = last_timestamp + timedelta(minutes=delta_minutes)

        generated_item = {'timestamp': timestamp.isoformat(), **generated_item}

        return generated_item, timestamp

    def _set_start_datetime(self, timestamp_meta):
        """ Set the starting datetime for the timestamp. """
        start_datetime = datetime.now()
       
        start_in = timestamp_meta.get('start_in', 'past').lower()
        start_window = Random.random_from_tuple(timestamp_meta.get('start_window', (0,0)))
        # print(f"start_window: {start_window}")
        if start_in == 'future':
            start_datetime += timedelta(minutes=start_window)
        elif start_in == 'past':
            start_datetime -= timedelta(minutes=start_window)
        else:
            raise ValueError("timestamp.start_in value must be 'future' or 'past'.")
        return start_datetime


    def _get_time_deltas(self, timestamp_meta):
        return map(int, timestamp_meta['timedelta(min)'].strip("()").split(","))




