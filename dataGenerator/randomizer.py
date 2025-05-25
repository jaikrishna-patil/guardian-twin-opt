import random
import string
import ast
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

class Random:
    def __init__(self):
        self.id_counters = {}
        self.last_for_set_range = {}
    #     already_selected = []

    data_gap = 0 # The percentage of missing data to generate
    

    @classmethod
    def set_data_gap_factor(cls, factor):
        cls.data_gap = factor
    
    @staticmethod
    def random_missing_data():
        empty = Random.data_gap
        filled = 100 - empty
        return random.choices([True, False], weights=[filled, empty])[0]

    @staticmethod
    def handle_random_fake(fake_value, indicator):
        if indicator == "*":
            return fake_value
        elif indicator == "!":
            return fake_value if Random.random_missing_data() else ""
        else:
            return indicator

    @staticmethod
    def fake_first_name(indicator):
        first_name = fake.first_name()
        return Random.handle_random_fake(first_name, indicator)

    @staticmethod
    def fake_last_name(indicator):
        last_name = fake.last_name()
        return Random.handle_random_fake(last_name, indicator)

    def fake_callsign(indicator):
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=3))
        callsign = f"{letters}{numbers}"
        return Random.handle_random_fake(callsign, indicator)

    def fake_street_address(indicator):
        street_address= fake.street_address()
        return Random.handle_random_fake(street_address, indicator)
    
    def fake_city(indicator):
        city = fake.city()
        return Random.handle_random_fake(city, indicator)
    
    def fake_state(indicator):
        state = fake.state()
        return Random.handle_random_fake(state, indicator)
    
    def fake_zipcode(indicator):
        zipcode = fake.zipcode()
        return Random.handle_random_fake(zipcode, indicator)
    
    def fake_phone_number(indicator):
        phone_number = fake.phone_number()
        return Random.handle_random_fake(phone_number, indicator)
    
    def fake_datetime(indicator):
        """Generate a fake datetime within the past 8 hours if the key is 'dateTime: "*"'.."""
        now = datetime.now()
        # Generate a random number of seconds within the past 8 hours
        seconds_past = random.randint(0, 8 * 60 * 60)
        # Subtract the random number of seconds from the current time
        past_datetime = now - timedelta(seconds=seconds_past)
        # Convert to ISO format string
        date_time_str = past_datetime.isoformat()
        return Random.handle_random_fake(date_time_str, indicator)

    def date_today(indicator):
        """Generate a date object for today if the key is 'date: "*"'."""
        date = datetime.now()
        date = date.strftime("%Y-%m-%d")
        print(f"date: {date}")
        return date
    
    def fake_time():
        """Generate a fake time in the past on today's date if the key is 'time: "*"'."""
        now = datetime.now()
        # Generate a random number of seconds to subtract, up to the current time of the day
        seconds_past = random.randint(0, now.hour * 3600 + now.minute * 60 + now.second)
        # Subtract the random number of seconds from the current time
        past_time = now - timedelta(seconds=seconds_past)
        # Format the time
        time_str = past_time.strftime("%H:%M:%S")
        print(f"time: {time_str}")
        return time_str
    
    def military_alphabet_phrase(length=5):
        military_alphabet = {
            'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo',
            'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliett',
            'K': 'Kilo', 'L': 'Lima', 'M': 'Mike', 'N': 'November', 'O': 'Oscar',
            'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
            'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray', 'Y': 'Yankee', 'Z': 'Zulu'
        }
        phrase = ' '.join(military_alphabet[random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')] for _ in range(length))
        return phrase
    
    
    @staticmethod
    def random_from_tuple(value):
        """Generate a random value within the range specified by a tuple string."""
        # Initialize the allow missing data indicator
        indicator = None

        # Convert value from string to tuple if it's a string
        if isinstance(value, str):
            if value.startswith("(") and value.endswith("!"):  # tuples that can be omitted are represented as (min, max)!
                value = value[:-1]
                indicator = "!"
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                raise ValueError("value is string and not a valid tuple representation")
        elif not isinstance(value, tuple):
            raise ValueError("value must be a tuple or a string that represents a tuple")

        # Ensure the tuple has exactly two elements
        if len(value) != 2:
            raise ValueError("tuple must have exactly two elements")

        min_val, max_val = value  # Use the tuple directly
        random_value = None

        # Check if the values are integer or floating-point
        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
            if isinstance(min_val, int) and isinstance(max_val, int):
                # Generate a random integer if both min and max are integers
                random_value = random.randint(min_val, max_val)
            else:
                # Generate a random floating-point number if either min or max is a float
                random_value = random.uniform(float(min_val), float(max_val))
                # Determine the number of decimal places in the input floats
                if isinstance(min_val, float) or isinstance(max_val, float):
                    decimal_places = max(len(str(min_val).split('.')[1]) if '.' in str(min_val) else 0,
                                         len(str(max_val).split('.')[1]) if '.' in str(max_val) else 0)
                    # Format the random value to match the number of decimal places
                    random_value = round(random_value, decimal_places)
        else:
            raise ValueError("min and max values must be numeric")

        if indicator == "!":
            return random_value if Random.random_missing_data() else None
        else:
            return random_value



    def parse_count(count):
        """Parse the "count" value from the metadata definitions."""
        if isinstance(count, tuple):
            return Random.random_from_tuple('count', count)
        elif isinstance(count, str) and count.startswith('(') and count.endswith(')'):
            count_tuple = ast.literal_eval(count)
            return Random.random_from_tuple('count', count_tuple)
        else:
            return int(count)

    def select_from_options(options, selection_type, already_selected=[]):
        """Select items from options based on selection_type, excluding already selected if unique."""
        options = [option for option in options if option not in already_selected]
        if selection_type == "single" or selection_type == "single!" or selection_type == "unique":
            selection = random.choice(options) if options else None
            if selection_type == "single!":
                selection = selection if Random.random_missing_data() else None
            return selection
        elif selection_type == "multiple" or selection_type == "multiple!":
            num_choices = random.randint(1, len(options))
            selections = random.sample(options, k=num_choices) if options else []
            if selection_type == "multiple!":
                selections = selections if Random.random_missing_data() else []
            return selections
        else:
            raise ValueError(f"Invalid selection_type: {selection_type}")