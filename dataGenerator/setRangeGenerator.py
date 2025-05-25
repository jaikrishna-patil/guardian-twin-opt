import random
import ast
from randomizer import Random
from utils import Utils
import math


class SetRangeGenerator:
    def __init__(self):
        self.last_for_set_range = {}

    def reset_set_range_trackers(self):
        """Reset the tracker for last_for_set_range."""
        self.last_for_set_range = {}
    
    @staticmethod
    def validate_set_range(set_range):

        if set_range is None:
            raise ValueError(f"_set_range cannot be empty.")
        
        if 'range' not in set_range or not isinstance(ast.literal_eval(set_range['range']), tuple):
            raise ValueError(f"_set_range must include a 'range' tuple param.")
        
        if 'max_delta' in set_range and not isinstance(set_range['max_delta'], (int, float)):
            raise ValueError(f"'max_delta' must be a number.")
        
        if 'average_speed(km/h)' in set_range and not isinstance(set_range['average_speed(km/h)'], (int, float)):
            raise ValueError(f"'average_speed(km/h)' must be a number.")
        
        if 'max_delta' not in set_range and 'average_speed(km/h)' not in set_range:
            raise ValueError(f"_set_range must include 'max_delta' or 'average_speed(km/h)' params.")
    
    def random_from_set_range(self, set_range, parent_node_name):
        """Generate a random number within the range specified by the _set_range key."""
        self.validate_set_range(set_range)
        
        range_tuple = ast.literal_eval(set_range['range'])
        max_delta = set_range.get('max_delta')
        average_speed = set_range.get('average_speed(km/h)')
        if average_speed:
            max_delta = self.speed_to_geocoord_rate(average_speed)
            # print(f"max_delta: {max_delta}")

        # If parent_node_name is in last_for_set_range, adjust the range based on max_delta
        if parent_node_name in self.last_for_set_range:
            last_value = self.last_for_set_range[parent_node_name]
            min_val, max_val = range_tuple
            adjusted_min = max(min_val, last_value - max_delta)
            adjusted_max = min(max_val, last_value + max_delta)
            # Ensure adjusted_min is not below min_val
            adjusted_min = max(adjusted_min, min_val)
            range_tuple = (adjusted_min, adjusted_max)

        # Generate a random value within the adjusted range
        random_value = Random.random_from_tuple(range_tuple)

        # Update last_for_set_range with the new value for the parent_node_name
        self.last_for_set_range[parent_node_name] = random_value

        # Return the generated random value
        return random_value
    
    @staticmethod
    def speed_to_geocoord_rate(speed_kmh):
        """
        Convert speed in km/h to a rate of change in geocoordinates per hour.
        
        :param speed_kmh: Speed in kilometers per hour
        """
        
        # Approximate degrees per km
        deg_per_km = 1 / 111
        
        # Calculate change in latitude and longitude per hour
        deg_per_hour = speed_kmh * deg_per_km
        
        return deg_per_hour
    
    # This is a more accurate method for deg/hr based on latitude.
    # def speed_to_geocoord_rate(speed_kmh, latitude):
    #     """
    #     Convert speed in km/h to a rate of change in geocoordinates per hour.
        
    #     :param speed_kmh: Speed in kilometers per hour
    #     :param latitude: Latitude in degrees where the movement is taking place
    #     :return: Tuple (lat_change_per_hour, lon_change_per_hour)
    #     """
    #     # Convert latitude to radians
    #     lat_rad = math.radians(latitude)
        
    #     # Approximate degrees per km
    #     deg_lat_per_km = 1 / 111
    #     deg_lon_per_km = 1 / (111 * math.cos(lat_rad))
        
    #     # Calculate change in latitude and longitude per hour
    #     lat_change_per_hour = speed_kmh * deg_lat_per_km
    #     lon_change_per_hour = speed_kmh * deg_lon_per_km
        
    #     return (lat_change_per_hour, lon_change_per_hour)