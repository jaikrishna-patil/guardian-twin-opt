from datetime import datetime, timedelta
import random
import ast
from randomizer import Random
from utils import Utils
from setRangeGenerator import SetRangeGenerator
# from dataProcessor import Process


TIMESTAMP_KEY = '_generate_timestamps'
class TimestampGenerator:
    def __init__(self, process_instance, Utils):
        self.process_instance = process_instance
        self.Utils = Utils
        self.counters = {}
        already_selected = []

    
    def generate_single_timestamp(self, base_datetime, schema, min_delta, max_delta, unique_selections):
        """ Generate a single timestamp object based on the timestamp schema.
            This function is called by the generate_timestamps_data() function and called recursively for each item in the schema.
        """
        timestamp_obj = {'timestamp': base_datetime.isoformat()}
        for key, value in schema.items():            
            self._process_schema_item(key, value, timestamp_obj, unique_selections)

        delta_minutes = random.randint(min_delta, max_delta)
        next_datetime = base_datetime + timedelta(minutes=delta_minutes)
        return timestamp_obj, next_datetime, unique_selections

    def generate_timestamps(self, node):
        timestamps = []
        if isinstance(node, dict):
            timestamp_meta = node.pop(TIMESTAMP_KEY, None)
            if timestamp_meta:
                total_timestamps = Random.random_from_tuple(timestamp_meta['count'])
                min_delta, max_delta = self._get_time_deltas(timestamp_meta)
                schemas_with_max_count = {}
                unique_selections = {}
                base_datetime = self._set_base_datetime(timestamp_meta)
                

                for _ in range(total_timestamps):
                    schema_path, schemas_with_max_count = self._get_schema_path(timestamp_meta, schemas_with_max_count)
                    if schema_path:
                        timestamp_obj, base_datetime = self.generate_and_append_timestamp(schema_path, base_datetime, min_delta, max_delta, unique_selections, timestamps)
        return timestamps
    
    def _set_base_datetime(self, timestamp_meta):
        base_datetime = datetime.now()
        if 'timestamp' in timestamp_meta:
            time_direction = timestamp_meta['timestamp'].get('time_direction', 'past').lower()
            start_window = Random.random_from_tuple(timestamp_meta['timestamp'].get('start_window', (0,0)))
            if time_direction == 'future':
                base_datetime += timedelta(minutes=start_window)
            elif time_direction == 'past':
                base_datetime -= timedelta(minutes=start_window)
            else:
                raise ValueError("Unsupported timestamp timedirection.  Must be 'future' or 'past'")
        return base_datetime


    def _get_time_deltas(self, timestamp_meta):
        return map(int, timestamp_meta['timestamp']['timedelta(min)'].strip("()").split(","))

    def _get_schema_path(self, timestamp_meta, schemas_with_max_count):
        schema_path = None
        if 'schemas' in timestamp_meta:
            all_schemas = timestamp_meta['schemas']
            schema_meta = random.choice(all_schemas)
            schema_key = str(schema_meta['schema'])  # Convert schema_meta to string to use as key
            if schema_key in schemas_with_max_count and schemas_with_max_count[schema_key]['max_count'] <= 0:
                return None, schemas_with_max_count
            schemas_with_max_count = self._update_max_count(schema_meta, schema_key, schemas_with_max_count)
            schema_path = schema_meta['schema']
        else:
            schema_path = timestamp_meta.get('schema')
        return schema_path, schemas_with_max_count

    def _update_max_count(self, schema_meta, schema_key, schemas_with_max_count):
        if 'max_count' in schema_meta:
            if schema_key not in schemas_with_max_count:
                schema_meta['max_count'] = Random.random_from_tuple(schema_meta['max_count']) - 1
                schemas_with_max_count[schema_key] = schema_meta
            else:
                schemas_with_max_count[schema_key]['max_count'] -= 1
        return schemas_with_max_count

    def generate_and_append_timestamp(self, schema_path, base_datetime, min_delta, max_delta, unique_selections, timestamps):
        loaded_schema = Utils.load_schema(schema_path)
        schema = loaded_schema if isinstance(loaded_schema, dict) else loaded_schema[0]
        timestamp_obj, next_datetime, unique_selections = self.generate_single_timestamp(base_datetime, schema, min_delta, max_delta, unique_selections)
        timestamps.append(timestamp_obj)
        return timestamp_obj, next_datetime

    def _process_schema_item(self, key, value, timestamp_obj, unique_selections):
        """ Process each item in the schema.
            This function is called by the generate_single_timestamp() function and called recursively for each item in the schema.
            Args:
                key: The key of the item in the schema.
                value: The value of the item in the schema.
                timestamp_obj: The timestamp object to be updated.
                unique_selections: A dictionary of unique selections for each key.
            
        """
        # Check if key or value is empty and return early if so
        if not key or value is None:
            return

        # Process the schema item based on its type
        if key == 'timestamp':
            return
        # elif key == 'location_label':
        #     timestamp_obj[key] = Random.military_alphabet_phrase(length=2)
        elif isinstance(value, str) and value.startswith("(") and value.endswith(")"):
            timestamp_obj[key] = Random.random_from_tuple(value)
        elif isinstance(value, list):
            self._process_list_value(key, value, timestamp_obj, unique_selections)
        elif isinstance(value, dict) and 'options' in value and 'selection_type' in value:
            self._process_dict_value(key, value, timestamp_obj, unique_selections)
        elif isinstance(value, dict) and '_set_range' in value:
            generator_function = self.process_instance.generator_tags.get('_set_range')
            if generator_function:
                # print(f"key: {key}")
                # print(f"value: {value}")
                timestamp_obj[key] = generator_function(key,value)
        else:
            timestamp_obj[key] = value



    def _process_list_value(self, key, value, timestamp_obj, unique_selections):
        """ Process a list value in the schema.
            This function is called by the process_schema_item() function and called recursively for each item in the schema.
        """
        selected_option = Random.select_from_options(value, "single" if len(value) == 1 else "multiple", unique_selections.get(key, []))
        timestamp_obj[key] = selected_option if isinstance(selected_option, list) else [selected_option]
        if 'unique' in value:
            unique_selections[key] = unique_selections.get(key, []) + [selected_option]



    def _process_dict_value(self, key, value, timestamp_obj, unique_selections):
        # Ensure unique_selections[key] is initialized as a list if not already
        if key not in unique_selections:
            unique_selections[key] = []
        selected_option = Random.select_from_options(value['options'], value['selection_type'], unique_selections[key])
        timestamp_obj[key] = selected_option
        if value['selection_type'] == 'unique':
            unique_selections[key].append(selected_option)


