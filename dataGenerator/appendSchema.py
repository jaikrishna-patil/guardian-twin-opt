import json
import random
from utils import Utils

class AppendSchema:
    def __init__(self):
        self.process_node = None
        self.utils = Utils()

    def select_random_schema(self, schemas):
        """Select a random schema from the list of schemas."""
        if schemas:
            return random.choice(schemas)
        return {}

    def append_schema_fields(self, node, schema):
        """Append fields of the selected schema to the node."""
        for key, value in schema.items():
            node[key] = value

    def process_appended_node(self, node):
        """Process the node to replace _append_schema with a randomly selected schema."""
        if '_append_schema' in node:
            schema_path = node['_append_schema']['schema']
            schemas = self.utils.load_schema(schema_path)
            selected_schema = self.select_random_schema(schemas)
            self.append_schema_fields(node, selected_schema)
            del node['_append_schema']
        
        return node
 