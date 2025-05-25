import json
import yaml
from datetime import datetime
import os
from utils import Utils
from dataProcessor import Process
from randomizer import Random
from idGenerator import IDGenerator
from setRangeGenerator import SetRangeGenerator

# Create a single instance of IDGenerator
# id_generator = IDGenerator()

def load_config(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

class DeepDataGenerator:
    def __init__(self, config):
        self.id_generator = IDGenerator()
        self.set_range_generator = SetRangeGenerator()
        self.config = config
        self.utils = Utils()
        self.process = Process()
        self._load_config_data()

    

    def _load_config_data(self):
        # Required parameters
        self.format = self.config.get('format')
        if self.format not in ['yaml', 'json']:
            raise ValueError("Invalid format specified. Must be 'yaml' or 'json'.")

        self.output_path = self.config.get('output_path')
        if not isinstance(self.output_path, str):
            raise ValueError("Invalid output_path specified. Must be a valid directory path.")

        # Create the output directory if it does not exist
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        
        self.scenarios_path = self.config.get('scenarios_path')
        if not isinstance(self.scenarios_path, str):
            raise ValueError("Invalid scenarios_path specified. Must be a valid file path.")

        # Optional parameters
        self.output_filename_prefix = self.config.get('output_filename_prefix', '')
        if not isinstance(self.output_filename_prefix, str):
            raise ValueError("output_filename_prefix must be a string.")

        self.specific_scenario_ids = self.config.get('specific_scenario_ids', [])
        if not all(isinstance(id, (str, int)) for id in self.specific_scenario_ids):
            raise ValueError("specific_scenario_ids must be an array of strings or integers.")

        # self.scenarios = Utils.load_schema(self.scenarios_path)
        self._load_scenarios_from_directory()

    def _load_scenarios_from_directory(self):
        self.scenarios = []
        for filename in os.listdir(self.scenarios_path):
            file_path = os.path.join(self.scenarios_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    if self.format == 'yaml':
                        scenarios = yaml.safe_load(file)
                    elif self.format == 'json':
                        scenarios = json.load(file)
                    else:
                        raise ValueError(f"Unsupported format: {self.format}")
                    self.scenarios.extend(scenarios)

    def _filter_scenarios(self):
        '''
        Filters the scenarios based on specific scenario IDs.
        If specific_scenario_ids are provided, it filters the scenarios list
        to include only the scenarios with matching IDs.
        '''
        if self.specific_scenario_ids:
            filtered_scenarios = []
            for scenario in self.scenarios:
                scenario_id = self._get_id_key_value(scenario)
                if scenario_id in self.specific_scenario_ids:
                    filtered_scenarios.append(scenario)
            self.specific_scenario_ids = [str(id) for id in self.specific_scenario_ids]  # Ensure all IDs are strings for comparison
            self.scenarios = [scenario for scenario in self.scenarios if str(self._get_id_key_value(scenario)) in self.specific_scenario_ids]

    def _process_scenario(self, scenario):
        """
        Processes a scenario and generate data based on the input schemas.

        Args:
            scenario (dict): The scenario to be processed.

        Raises:
            ValueError: If the scenario does not have a key with the suffix '_id' or '_ID'.

        Returns:
            None
        """
        

        scenario_id = self._get_id_key_value(scenario)
        if scenario_id is None:
            raise ValueError("Scenarios must have a key with the suffix '_id' or '_ID'.")

        output_filename = str(scenario_id) if self.output_filename_prefix is None else self.output_filename_prefix + str(scenario_id)
        scenario_output_path = os.path.join(self.output_path, output_filename)
        Utils.ensure_directory_exists(scenario_output_path)
        print("  ")
        print(f"Scenario_{scenario_id}: {scenario['name']}")
        self._generate_scenario_reference(self.format, scenario_id, scenario, scenario_output_path, self.output_filename_prefix)

        for input_schema in scenario['input_schemas']:
            self._process_input_schema(input_schema, scenario_output_path)
    
    def write_data_to_file(self, output_file_path, data, format):
        if format == 'yaml':
            with open(output_file_path, 'w') as outfile:
                yaml.dump(data, outfile, Dumper=CustomDumper, allow_unicode=True, default_flow_style=False, indent=4, sort_keys=False)
        elif format == 'json':
            with open(output_file_path, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_data(self, schema_path, scenario_output_path, all_iterations_output, num_iterations, data_gap):
        output_file_name = Utils.set_output_file_name(schema_path, self.format)
        output_file_path = os.path.join(scenario_output_path, output_file_name)

        self.write_data_to_file(output_file_path, all_iterations_output, self.format)

        schema_base_name = os.path.basename(schema_path)
        print(f"- `{schema_base_name}`: {num_iterations} instances generated {f'with {data_gap}% missing data ' if data_gap else ''}")
    
    def _process_input_schema(self, input_schema, scenario_output_path):
        """
        Process the input schema and generate data based on the specified parameters.

        Args:
            input_schema (dict): The input schema containing the path, iterations, and optional data_gap.
            scenario_output_path (str): The path to the scenario output directory.
        """
        self.set_range_generator.reset_set_range_trackers()

        schema_path = input_schema['path']
        num_iterations = input_schema['iterations']
        data_gap = 0  # (0-100) Percentage of data to be missing for select params

        # Check if data_gap is specified in the input schema
        if 'data_gap' in input_schema:
            data_gap = input_schema['data_gap']

        # Set the missing data factor for various classes
        Random.set_data_gap_factor(data_gap)

        # Set the number of iterations for various classes
        IDGenerator.set_number_of_iterations(num_iterations)

        all_iterations_output = []  # Initialize an empty list to hold all iterations

        # Iterate through the number of iterations
        for iteration in range(num_iterations):
            schema = Utils.load_schema(schema_path)

            processed_schema = self.process.process_node(schema)
            all_iterations_output.append(processed_schema)  # Append the processed schema to the list

        # Write the list of all processed schemas to a single output file
        self.generate_data(schema_path, scenario_output_path, all_iterations_output, num_iterations, data_gap)


    def generate_scenario_data(self):
        self._load_config_data()
        self._filter_scenarios()
        
        print(f"Generating data for {len(self.scenarios)} scenarios...")
        print(f"Go to config_dataGenerator.yaml and change ")
        for scenario in self.scenarios:
            self.id_generator.reset_uuids()
            self._process_scenario(scenario)
        print("DONE: All test case data generated.")
        print(" ")

    def _generate_scenario_reference(self, format, scenario_id, test_case, output_path, output_filename_prefix):
        output_filename = str(scenario_id) if output_filename_prefix is None else '_'+ output_filename_prefix + str(scenario_id)
        reference_file_path = os.path.join(output_path, output_filename + f'.{format}')
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the current datetime as a string
        
        if format == 'yaml':
            with open(reference_file_path, 'w') as reference_file:
                reference_file.write(f"# Data generated at {current_datetime}\n")  # Write the comment at the top
                yaml.dump(test_case, reference_file, allow_unicode=True, default_flow_style=False, indent=4, sort_keys=False)
        elif format == 'json':
            with open(reference_file_path, 'w') as reference_file:
                comment = f"// Data generated at {current_datetime}\n"  # JSON does not officially support comments, but this can be useful for developers
                json_content = json.dumps(test_case, indent=4)
                reference_file.write(comment + json_content)
    
    @staticmethod
    def _get_id_key_value(data):
        for key in data.keys():
            if key.endswith("_id") or key.endswith("_ID"):
                return data[key]  # Return the value of the first matching key
        return None  # Return None if no matching key is found


class CustomDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)
    
    def ignore_aliases(self, data):
        return True  # This will ignore aliases for all data types


if __name__ == "__main__":
    # See dataGenerator_config.yaml in root
    config_path = './_config_dataGenerator.yaml'
    config = load_config(config_path)
    # Initialize ScenarioGenerator with config
    generator = DeepDataGenerator(config)
    # Call generate_scenario_data without 'self'
    generator.generate_scenario_data()

