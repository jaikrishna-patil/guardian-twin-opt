from services.service_adaptive_resource_opt.algos.AlgoAdaptiveResourceOpt import AdaptiveResourceOpt

from enum import Enum


class AlgoName(Enum):
    ADAPTIVE_RESOURCE_OPT='adaptive_resource_opt'

class FactoryAlgos:

    @staticmethod
    def create_algo(mode:str):
        if mode == AlgoName.ADAPTIVE_RESOURCE_OPT:
            return AdaptiveResourceOpt()

        else:
            raise ValueError("Invalid mode or missing configuration for advanced mode.")