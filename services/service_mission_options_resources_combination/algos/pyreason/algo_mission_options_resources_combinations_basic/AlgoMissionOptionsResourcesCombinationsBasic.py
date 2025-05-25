from services.service_mission_options_resources_combination.AlgoMissionOptionsResourcesCombination import OptionsResourcesCombination

from services.models.ModelMissionOptionsResourcesCombinations import MissionOptionsResourcesCombinations
from services.models.ModelMissionRequirements import MissionRequirements
from services.models.ModelCareFacility import CareFacility
from services.models.ModelAsset import Asset
from services.models.ModelMissionOptionsAssets import MissionOptionsAssets

from datetime import datetime
import networkx as nx
import pyreason as pr
import os

class MissionOptionsResourcesCombinationBasic(OptionsResourcesCombination):

    def __init__(self):
        self.interpretation = None
        self.next_time = 0

    def get_pyreason_bool(self, python_bool: bool) -> str:
        if python_bool:
            return '1,1'
        else:
            return '0,0'
    def create_pyreason_graph(self,assets: list[Asset], care_facilities: list[CareFacility],
                              mission_options_assets: list[MissionOptionsAssets], mission_requirements: list[MissionRequirements]):
        g = nx.DiGraph()

        return g
    def write_graphml(self, nx_graph, graphml_path: str):
        nx.write_graphml_lxml(nx_graph, graphml_path, named_key_ids=True)

    def return_mission_options_resources_combinations(self, assets: list[Asset], care_facilities: list[CareFacility],
                                                      mission_options_assets: list[MissionOptionsAssets], mission_requirements: list[MissionRequirements])\
            -> list[MissionOptionsResourcesCombinations]:


        mission_options_resources_combinations = []
        # Set pyreason settings


        return mission_options_resources_combinations


