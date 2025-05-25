import random
import uuid
from utils import Utils
from randomizer import Random

class IDGenerator:
    _instance = None
    num_iterations = 0 
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IDGenerator, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.counters = {}
            # self.isop_ids = []
            # self.current_index = 0
            self.generated_uuids = {}
            self.current_uuid_indexes = {}
            self.selected_uuids = {}
            self.initialized = True
    
    def reset_isop_ids(self):
        self.isop_ids = []
    
    def reset_indexes(self):
        self.current_index = 0
    
    def reset_generated_uuids(self):
        self.generated_uuids = {}
    
    def reset_current_uuid_indexes(self):
        self.current_uuid_indexes = {}
    
    def reset_selected_uuids(self):
        self.selected_uuids = {}
    
    def reset_uuids(self):
        self.reset_generated_uuids()
        self.reset_current_uuid_indexes()
        self.reset_selected_uuids()
    
    @classmethod
    def set_number_of_iterations(cls, number_of_iterations):
        cls.num_iterations = number_of_iterations
        
    def generate_uuid(self, node_dict):
        """
        Generate a UUID based on the _generate_uuid specifications.

        :param node: The node containing the_generate_uuid key.
        :return: The generated UUID as a string.
        """
        id_meta = node_dict.pop('_generate_uuid', None)
        new_uuid = str(uuid.uuid4())

        if isinstance(id_meta, str):
            if id_meta not in self.generated_uuids:
                self.generated_uuids[id_meta] = []
            self.generated_uuids[id_meta].append(new_uuid)
        return new_uuid

    def get_id(self, node_dict):
        """
        Retrieve a UUID generated for isop_details and assign it to isop_id for isop_state.

        :param node_dict: The node containing the _get_id key.
        :return: The UUID as a string if _get_id matches "isop_id"; otherwise, None.
        """
        get_id_spec = node_dict.pop('_get_id', None)

        if isinstance(get_id_spec, str):
            if get_id_spec not in self.current_uuid_indexes:
                self.current_uuid_indexes[get_id_spec] = 0

            if get_id_spec in self.generated_uuids:
                if self.current_uuid_indexes[get_id_spec] < len(self.generated_uuids[get_id_spec]):
                    uuid = self.generated_uuids[get_id_spec][self.current_uuid_indexes[get_id_spec]]
                    self.current_uuid_indexes[get_id_spec] += 1
                    return uuid
                else:
                    print(f"get_id_spec:{get_id_spec}")
                    print(f"Warning: No available UUIDs to assign for {get_id_spec}.")
                    return None
        return None
    
    def get_ids(self, node_dict):
        """
        Return random length arrays of specific ids based on the _get_ids metadata.
        :param node_dict: The node containing the _get_ids key.
        :return: A list of ids of random length specified by the count in _get_ids metadata.
        """
        # Extract _get_ids metadata and remove it from node_dict
        get_ids_meta = node_dict.pop('_get_ids', None)
        # print(f"get_ids_meta: {get_ids_meta}")
        if not get_ids_meta:
            print("No _get_ids metadata found.")
            return []
        
        id_name = get_ids_meta.get('id_name')
        count_range = get_ids_meta.get('count', (0,))  # Default to a tuple with a single zero if not specified
        # print(f"id_name: {id_name}, count_range: {count_range}")
        
        # Randomly pick a count from the count_range tuple
        count = Random.random_from_tuple(count_range)
        # print(f"Randomly selected count: {count}")
        

        if id_name in self.generated_uuids:
            total_ids = len(self.generated_uuids[id_name])
            current_index = self.current_uuid_indexes[id_name]
            # print(f"length of generated_uuids: {total_ids}")
            if total_ids == 0:
                print(f"Warning: No available UUIDs to assign for {id_name}.")
                return []
            
            if id_name not in self.current_uuid_indexes:
                current_index = 0

            # Reset current_uuid_indexes if it exceeds the length of generated_uuids
            if current_index >= total_ids:
                current_index = 0
            
            # Calculate the maximum number of ids that can be assigned per iteration
            max_ids_per_iteration = total_ids // IDGenerator.num_iterations
            max_ids_per_iteration = max(1, max_ids_per_iteration)

            
            # Randomly pick a count from the count_range tuple, considering the max_ids_per_iteration
            count = min(count, max_ids_per_iteration)

            
            # Ensure count does not exceed limit of available ids
            available_ids = total_ids - current_index

            count = min(count, available_ids)

            # Ensure count does not exceed total_ids
            count = min(count, total_ids)
            
            

            if id_name not in self.selected_uuids:
                self.selected_uuids[id_name] = []
            num_ids_selected = len(self.selected_uuids[id_name])
            ids_needed = total_ids - num_ids_selected
            # Ensure count will meet ids_needed
            # count = min(count, ids_needed)

            selected_ids = []
            for _ in range(count):
                if current_index < total_ids:
                    selected_id = self.generated_uuids[id_name][current_index]
                    selected_ids.append(selected_id)
                    self.selected_uuids[id_name].append(selected_id)
                    current_index += 1
                else:
                    break
            
            # Update the current index for the next iteration
            self.current_uuid_indexes[id_name] = current_index
            
            # print(f"length selected_uuids {id_name}: {num_ids_selected}")
            return selected_ids
        
        # If id_name does not match any known id collections, return an empty list
        print(f"id_name {id_name} does not match any known id collections.")
        return []
    ...

    def generate_id(self, node_dict):
        """
        Generate an ID based on the _generate_id specifications.

        :param node: The node containing the_generate_id key.
        :return: The generated ID as a string, ensuring it meets the min_length requirement.
        """
        # _generate_id: {type: <type='sequential' or 'random'>, start: <int>, increment: <int>, min_length: <int>}
        

        id_meta = node_dict.pop('_generate_id', None)
      
        if id_meta['type'] == 'sequential':
            # Convert node_dict to a hashable object (tuple of tuples sorted by key to ensure consistency)
            node_dict_hashable = Utils.make_hashable(node_dict)

            # Initialize the counter for this ID if it hasn't been already
            if node_dict_hashable not in self.counters:
                self.counters[node_dict_hashable] = id_meta['start']
            else:
                self.counters[node_dict_hashable] += id_meta['increment']

            generated_id = str(self.counters[node_dict_hashable])
        elif id_meta['type'] == 'random':
            # Generate a random ID between the start value and a large number, assuming start is the minimum
            generated_id = str(random.randint(id_meta['start'], id_meta['start'] + 1000000))
        else:
            raise ValueError("Unsupported ID generation type")

        # Ensure the generated ID meets the min_length requirement
        min_length = id_meta.get('min_length', 1)
        generated_id = generated_id.zfill(min_length)
      
        return int(generated_id) if id_meta['type'] == 'sequential' else generated_id