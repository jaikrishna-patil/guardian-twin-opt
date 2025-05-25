import os
import yaml

class Utils:
    def __init__(self):
        pass
    
    @staticmethod
    def ensure_directory_exists(directory):
        """Ensure the output directory exists."""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def load_schema(schema_path):
        """Load and return the schema from a YAML file."""
        file_extension = os.path.splitext(schema_path)[1].lower()
        if file_extension == '.yaml' or file_extension == '.yml':
            try:
                with open(schema_path, 'r') as schema_file:
                    return yaml.safe_load(schema_file)
            except yaml.YAMLError as e:
                print(f"Error loading YAML schema from {schema_path}: {e}")
                return None
        elif file_extension == '.json':
            print("JSON not supported yet.")
            return None
        else:
            print(f"Unsupported file extension: {file_extension}")
            return None

    # def load_json_schemas(self, schema_path):
    #     """Load schemas from the specified file."""
    #     try:
    #         with open(schema_path, 'r') as file:
    #             schemas = json.load(file)
    #         return schemas
    #     except (FileNotFoundError, json.JSONDecodeError) as e:
    #         print(f"Error loading schemas from {schema_path}: {e}")
    #         return []
    
    @staticmethod
    def make_hashable(obj):
        if isinstance(obj, dict):
            return tuple(sorted((k, Utils.make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, list):
            return tuple(Utils.make_hashable(v) for v in obj)
        else:
            return obj
        
    @staticmethod
    def set_output_file_name(input_schema_path, file_format):
        schema_base_name = os.path.basename(input_schema_path).split('.')[0]  # Extract base name without extension
        plural_schema_base_name = schema_base_name + 's'  # Simple pluralization by appending 's'
        output_file_name = plural_schema_base_name + '.' + file_format  # Construct output file name
        return output_file_name
    

