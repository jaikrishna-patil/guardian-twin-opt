# OVERVIEW

This system generates data according to specifications in a listof Scenarios.
Each Scenario is a dictionary that contains metadata about the scenario and an array of input schemas to generate data for.
You can specify the number of iterations to generate data for each input schema as well as the percentage of data to be missing.
Data for each input schema is generated recursively, so the schemas can be nested and quite complex and even reference other schemas.
The actual data generation uses a library of special values and '_generator_tags' that trigger corresponding methods.
Finally, generated data is saved to specific directories in the `../test_data` directory.
TODO: Update when generated data is saved to a database.
TODO: Link to demo video here
<!-- <video width="320" height="240" controls>
  <source src="URL_TO_VIDEO" type="video/mp4">
  Your browser does not support the video tag.
</video> -->

***

## GETTING STARTED

Ensure your environment is `python 3.10.5`
From the project `root`, run `pip install -r requirements.txt` to install the required packages.
Navigate to `../dataGenerator/config_dataGenerator.yaml` to customize path references, naming conventions, and other params
Setup scenario files at desired path, default is `../dataSchemas/_scenarios`
Each scenario file may contain an array of scenarios.
Once you have scenarios setup, run `python generateData.py` (located in `../dataGenerator/`)

***

## SETTING UP TEST SCENARIOS

Navigate to the directory specified by `_config_dataGenerator.py` `scenarios_path`.  Default is `../dataSchemas/_scenarios/`.
In this directory, create one or many test scenario yaml files.
Each test scenario yaml file may contain a list of scenarios.
Only the fields noted as REQUIRED are required and used for data generation.
Additional fields can be added to help desribe the intent of the scenario, or used to spec certain values for the scenario, eg "constraints" in example below. 

Example Test Scenario Schema:

```yaml
- scenario_id: # REQUIRED - Keep it simple, like 1 or 1a.  Specific IDs can be noted in the config_dataGenerator.yaml to generate data for specific scenarios 
  name: # REQUIRED - Will be the name of the output directory in ../test_data/
  description: # A brief description of the test case
  inputs: # Overview of the data to consider
  outputs: # Overview of the intended output for the scenario
  output_files: # references to schemas that should be used for scenario data processing output
  success_criteria: # The expected functionality to be developed and tested
  input_schemas: # REQUIRED - A list of input schemas to generate test data for
    - path: # REQUIRED - The path to the input schema from ../schemas
      iterations: # REQUIRED - The number of iterations to generate test data for
      data_gap: # (0-100) Percentage of data to be missing for select params in that schema
  constraints: # a list of constraints meta that should be applied when processing the scenario data
```

***

## GENERATING TEST SCENARIO DATA

To generate test data for all test scenarios...

- in your terminal run: `python generateData.py`
- `generateData.py` is located in `../dataGenerator`

To generate test data for specific scenarios, navigate to `../dataGenerator/config_dataGenerator.yaml` and enter the scenario ids into `specific_scenario_ids` array.
TODO: Enable scenario ids as arg for generateData.py

***

## CREATING DATAGEN SCHEMAS

This system uses a library of special syntax, special fields, and generator tags to indicate how data should be generated.

### Special Keys

The following keys in schemas have special methods to generate corresponding data:

```yaml
# * - ignores data_gap settings
# ! - observes data_gap settings
first_name: < "*" or "!" > # Generates a random first name.
last_name: < "*" or "!" > # Generates a random last name.
callsign: < "*" or "!" > # Generates a random callsign.
dateTime: < "*" or "!" > # Generates a random datetime.
date: < "*" or "!" > # Generates a random date.
time: < "*" or "!" > # Generates a random time.
# TODO: Add complete list
```

<br>

### Random Value from Tuple Ranges

If you want to specify a range for key, you can use tuples, like:

```yaml
range: (min, max) # A random value from the range will be generated, data_gap is ignored.
range: (min, max)! # As above, but data_gap settings observed
# min, max may be <int> or <float>

# Examples:
heart_rate: (60, 120)! # May return a random value between 60 - 120.  However, it may sometimes be empty due to the "!" introducing data_gap

latitude: (31.33, 42.00) # Will return a random float between 31.33 - 42.00.  It will ignore any data_gap settings.

```


<br>

### Generate Simple Lists

For simple lists, you can use the following syntax:

```yaml
list_of_options:
  selection_type: # The type of selection to perform. (single, multiple) ignores data_gap or (single!, multiple!) observes data_gap.
  options: # The list of options to select from.
    - option1
    - option2
    - option3

# Examples:
favorite_colors:
  selection_type: multiple   # Will return favorite_colors with one or more options, eg favorite_colors: [blue, green]
  options:
    - red
    - blue
    - green

favorite_superhero:
  selection_type: single! # May return favorite_superhero with one option, eg favorite_superhero: Venom.  However, it may also be empty
  options:
    - Dead Pool
    - Venom
    - Iron Man
```

**NOTE:** For more complex list options, use `_generate_list` to generate complex lists using other schemas: (see below)

<br>

### How to Generate IDs

To generate UUIDs, use the `_generate_uuid` generator tag:

```yaml
#Example
user_id:
  _generate_uuid: # will generate a uuid, eg 2d3e4f5g-6h7i-8j9k-0l1m-2n3o4p5q6r7s
```  

<br>

### How to reference generated IDs in other schemas

If you want to reference generated UUIDS in other schemas use the `_get_uuid` generator tag.
Note this isn't well tested or protected yet, so proceed with caution and follow these steps:

- In the scenario.input_schemas, be sure to run a schema with a `_generate_uuid` tag prior to a schema with a `_get_uuid` tag.
- In the 'generating' schema, ensure that you specify a unique UUID label, eg `_generate_uuid: "user_id"`
- In the 'getting' schema, specify the uuid label you want to retrieve IDs from, eg `_get_uuid: "user_id"`.
- NOTE: `_get_uuid` simply iterates through the specified list created by `_generate_uuid` and sequentially retrieves IDs
- Therefore, it is best to ensure that both schemas have the same number of iterations.
- For example, if I generate 10 x user_ids via a user_profile schema, then for schemas with `_get_uuid: "user_id` tags, I should also run 10 iterations.
- NOTE: the UUID lists reset between each scenario.  Only hard coded IDs will persist from scenario to scenario. 

Example:

```yaml
# user_profile.yaml
user_id: # The key to assign the UUID to, eg output will be user_id: 2d3e4f5g-6h7i-8j9k-0l1m-2n3o4p5q6r7
  _generate_uuid: "user_id" # The identifier to assign the UUID to.

# user_actions.yaml
user_id: # The key to assign the UUID to, eg output will be user_id: 2d3e4f5g-6h7i-8j9k-0l1m-2n3o4p5q6r7
  _get_id: "user_id" # The uuid list name identifier to get UUID from.

```

<br>

To generate simple sequential or random IDs, use the following syntax:**

```yaml
_generate_id:
  type: <'sequential' or 'random'> # The type of ID generation.
  start: <int> # The starting value of the ID.
  increment: <int> # The increment value of the ID.
  min_length: <int> # The minimum length of the ID.
```

### How to Generate Complex Lists

To generate a list from a single schema, use the following syntax:

```yaml
parent_node: # receives the generated list
  _generate_list: 
    schema: <path>  # The path to the schema to generate a list from.
    count: <tuple>  # The number of items to generate.
    # unique_instances: <bool>  # If True, ensure uniqueness of items in the list
    # append: <path>  # The path to another schema to append to list items, like a timestamp schema
    # schemas

# Example Schema:
favorite_movies:
  _generate_list:
    schema: '../movie_schema.yaml'
    count: (1,3)

# Example Return:
favorite_movies:
  - label: Indiana Jones
    year_released: 1981
  - label: 28 Days Later
    year_released: 2003
```

TODO: Add support for appending to list items.
TODO: Add support for generating a list from multiple schemas like _generate_timestamps.

### How to Generate Complex Timestamps

To generate a list of timestamps from a schema, you can reuse `_generate_list` and include a `timestamp` param with options.

```yaml
parent_node: # receives the list of timestamps
  _generate_list:
    schema: <path>  # The path to the schema to generate a timestamp list from. NOTE: a 'timestamp' parameter will be added at the top of each instance generated from the schema.
    count: <tuple>  # The number of items to generate
    timestamp: 
      timedelta(min): <tuple> # range of minutes to randomly increment timestamps
      start_in: <string> # options: future or past.  When to start the timestamps.
      start_window: <tuple> # range of minutes to randomly start the timestamps from in the future or past.
      ## For example: if start_in=past and start_window=(60,120) and time_delta(min)=(5,30), then timestamps will be generated from a starting point 1-2 hours in the past from NOW, and then only increment forward in time from that initial timestamp by some random amount of time between 5 to 30 minutes.
```

TODO: Update start_window to start_window(min)

### How to Set Confined Movement Distances

You can use the `_set_range` generator tag to generate data with reasonablility constraints.
We can define a max_delta, similar to timedelta, that once the initial random value in the range is set, each subsequent value can only move up or down by some random number within the max_delta.
If we want to generate reasonable data for the mode of movement (eg: walking, running, driving, flying, etc.) we can ommit max_delta and instead provide average_speed(km/h).
NOTE: this still needs some work to account for the timedelta between each instance.

```yaml
parent_node: # Receive a semi-random value within the range, constrained by max_delta or average_speed.
  _set_range:
    range: <tuple> # Some set of numbers 
    max_delta: <int> or <float> # The max delta between each lat and long points, for example to simulate likely walking, running, driving, flying speeds
    average_speed(km/h): <int>

# Examples:
latitude:
  _set_range:
    range: (31.33, 42.00) # decimal degrees...southern border of AZ to northern border of UT
    average_speed(km/h): 280 # average speed of a blackhawk helicopter

elevation:
  _set_range:
    range: (0, 3000) # meters
    max_delta: 50
```
TODO: confirm max_delta is indeed randomized for each instance
TODO: if average_speed, validate that range is valid lat or long coordinates
TODO: if average_speed, validate that timedelta is being considered.  

### How to Generate Custom Names

You can use the `_generate_custom_names` generator tag to generate unique name
```yaml
parent_node: # Receives the generated name
  _generate_custom_name:
    prefix: <string> # Any string you want, eg "Location_"
    suffix: <string> # A specific string that indicates the type of generator to use, currently just "Military Alphabet"

# Example:
location_name: # Receives the generated name, eg "Location_Alpha"
  _generate_custom_name:
    prefix: "Location_"
    suffix: "Military Alphabet"
```
