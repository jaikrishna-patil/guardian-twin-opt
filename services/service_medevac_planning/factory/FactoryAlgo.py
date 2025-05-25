
from services.service_medevac_planning.algos.algo_final_assignment.algo_multiple_obj.AlgoMedevacPlanning import MedevacPlanning
from services.service_medevac_planning.algos.algo_final_assignment.algo_multiple_obj.AlgoMedevacSchedule import MedevacSchedule
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class AlgoName(Enum):
    MEDEVAC_PLAN = 'medevac_plan'
    MEDEVAC_SCHEDULE = 'medevac_schedule'

class FactoryAlgos:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_algo(mode:str):
        if mode == AlgoName.MEDEVAC_PLAN:
            return MedevacPlanning()
        if mode == AlgoName.MEDEVAC_SCHEDULE:
            return MedevacSchedule()



        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")