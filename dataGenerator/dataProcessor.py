import re
from randomizer import Random
from idGenerator import IDGenerator
from listGenerator import ListGenerator
from timestampGenerator import TimestampGenerator
from setRangeGenerator import SetRangeGenerator
from customNameGenerator import CustomNameGenerator
from utils import Utils
from appendSchema import AppendSchema


class Process:
    def __init__(self):
        # self.counters = {}
        self.id_generator = IDGenerator()
        self.list_generator = ListGenerator(self)
        self.timestamp_generator = TimestampGenerator(self, Utils)
        self.set_range_generator = SetRangeGenerator()
        self.custom_name_generator = CustomNameGenerator()
        self.append_schema = AppendSchema()
        self.special_keys = {
            "first_name": Random.fake_first_name,
            "fName": Random.fake_first_name,
            "firstName": Random.fake_first_name,
            "last_name": Random.fake_last_name,
            "lName": Random.fake_last_name,
            "lastName": Random.fake_last_name,
            "callsign": Random.fake_callsign,
            "date": Random.date_today,
            "dateTime": Random.fake_datetime,
            "last_updated": Random.fake_datetime,
            "lastUpdated": Random.fake_datetime,
            "updated": Random.fake_datetime,
            "created": Random.fake_datetime,
            "time": Random.fake_time, # some random time in the past on today's date
            "street_address": Random.fake_street_address,
            "street": Random.fake_street_address,
            "streetAddress": Random.fake_street_address,
            "city": Random.fake_city,
            "state": Random.fake_state,
            "zipcode": Random.fake_zipcode,
            "zip": Random.fake_zipcode,
            "phone_number": Random.fake_phone_number,
            "phoneNumber": Random.fake_phone_number
        }
        self.generator_tags = {
            '_generate_uuid': self.id_generator.generate_uuid,
            '_generate_id': self.id_generator.generate_id,
            '_get_id': self.id_generator.get_id,
            '_get_ids': self.id_generator.get_ids,
            '_generate_list': self.list_generator.generate_list,
            '_generate_timestamps': self.timestamp_generator.generate_timestamps,
            '_set_range': self.set_range_generator.random_from_set_range,
            '_generate_custom_name': self.custom_name_generator.generate_custom_name,
            '_append_schema': self.append_schema.process_appended_node
        }
        # TODO: _get_single_item

    # Process the node in the schema
    def process_node(self, node, parent_key=None):
        """
        Recursively process each node based on its type and specific keys.

        Args:
            node: The node to be processed.
            parent_key: The key of the parent node.

        Returns:
            The processed node.

        """
        
        if isinstance(node, dict):
            parent_key = ""
            for key in node:
                if isinstance(node[key], dict):
                    for sub_key in node[key]:
                        if sub_key in self.generator_tags:
                            parent_key = key  # Set parent_key to the current key
                            if sub_key == "_set_range":
                                return self.process_dict(node[key], parent_key)
            return self.process_dict(node, parent_key)
        elif isinstance(node, list):
            return [self.process_node(item, parent_key) for item in node]
        else:
            # Directly return the node if it's neither a dict nor a list
            return node

    def process_dict(self, node_dict, parent_key):
        """Process a dictionary node, applying specific logic based on keys.

        Args:
            node_dict (dict): The dictionary node to be processed.
            parent_key (str): The key of the parent node..

        Returns:
            dict: The processed dictionary node.

        """
        processed_node = {}
        # print(f"parent_key:{parent_key}")
        # TODO: Refactor to def handle_generator_tags(self, node_dict):
        # Handle the generator_tags
        generator_tags = self.generator_tags
        
        for key in generator_tags:
            if key in node_dict:

                if key == '_set_range':
                    generated_data = generator_tags[key](node_dict, parent_key)
                # elif key == '_append_schema':
                #     print('_append_schema')
                    
                #     generated_data = generator_tags[key](node_dict)
                #     print(f"generated_data:{generated_data}")
                else:
                    generated_data = generator_tags[key](node_dict)
                
                if isinstance(generated_data, dict):
                    processed_node.update(generated_data)  # Update processed_node with the generated data if it's a dict
                elif isinstance(generated_data, list):
                    processed_node = generated_data  # Update processed_node with the generated data
                elif key == '_generate_uuid' and isinstance(generated_data, str):
                    # self.isop_ids.append(generated_data)
                    processed_node = generated_data  # Update processed_node with the generated data
                elif key == '_get_id' and isinstance(generated_data, str):
                    processed_node = generated_data  # Update processed_node with the generated data
                elif isinstance(generated_data, (str, float)):
                    processed_node = generated_data
                elif key == '_generate_id' and isinstance(generated_data, str) or isinstance(generated_data, int):
                    processed_node = generated_data  # Update processed_node with the generated data
                else:
                    # Handle the case where generated_data is neither a dictionary nor a list
                    print(f"Unexpected generated_data type: {type(generated_data)}")

        for key, value in node_dict.items():
            try:
                # TODO: Refactor to def handle_special_keys(self, node_dict):
                # Handle the special_keys
                if key in self.special_keys:
                    processed_node[key] = self.special_keys[key](value)

                # TODO: Refactor to handle_other_types(self, node_dict):
                # Handle other types of values 
                elif isinstance(value, str) and re.match(r"\(-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?\)!?", value):
                    # print(f'tuple value: {value}')
                    processed_node[key] = Random.random_from_tuple(value)
                elif isinstance(value, dict) and 'options' in value and 'selection_type' in value:
                    processed_node[key] = Random.select_from_options(value['options'], value['selection_type'])
                elif isinstance(value, dict) or isinstance(value, list):
                    # Skip processing for '_timestampMeta' and '_listGenMeta' keys as they're already handled
                    if key not in generator_tags:
                        processed_node[key] = self.process_node(value)
                else:
                    processed_node[key] = value
            except ValueError as e:
                print(f"Error processing {key}: {e}")
        return processed_node