
from services.service_optimization.algos.algo_final_assignment.algo_multiple_obj.AlgoOptimizationMultipleObj import OptimizationMultipleObj
from services.service_optimization.algos.algo_final_assignment.algo_multiple_obj.AlgoOptimizationSingleObj import OptimizationSingleObj
from services.service_optimization.algos.algo_final_assignment.algo_multiple_obj.AlgoOptimizationSingleObjScheduler import OptimizationSingleObjScheduler
from services.service_optimization.algos.algo_final_assignment.algo_multiple_obj.AlgoOptimizationMultipleObjScheduler import OptimizationMultipleObjScheduler
from services.service_optimization.algos.algo_final_assignment.algo_multiple_obj.AlgoOptimizationMultipleObjMultipleConstraints import OptimizationMultipleObjMultipleConstraints
from typing import Dict
from pydantic import BaseModel
from enum import Enum


class AlgoName(Enum):
    MULTIPLE_OBJ = "multiple_obj"
    SINGLE_OBJ = "single_obj"
    SINGLE_OBJ_SCHEDULER = "single_obj_scheduler"
    MULIPLE_OBJ_CONSTRAINT = "multiple_obj_constraint"
    MULTIPLE_OBJ_SCHEDULER = "multiple_obj_scheduler"

class FactoryAlgos:
    """
    Overview - As we develop more Triage Algos, we simply append this list.  Ultimately, this could be driven from config or made to be dynamic
    """
    @staticmethod
    def create_algo(mode:str):
        if mode == AlgoName.MULTIPLE_OBJ:
            return OptimizationMultipleObj()
        if mode == AlgoName.SINGLE_OBJ:
            return OptimizationSingleObj()
        if mode == AlgoName.SINGLE_OBJ_SCHEDULER:
            return OptimizationSingleObjScheduler()
        if mode == AlgoName.MULIPLE_OBJ_CONSTRAINT:
            return OptimizationMultipleObjMultipleConstraints()
        if mode == AlgoName.MULTIPLE_OBJ_SCHEDULER:
            return OptimizationMultipleObjScheduler()



        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")