from abc import ABC, abstractmethod
from typing import Dict, List

from pandas import DataFrame


class AbstractOptimizer(ABC):
    def __init__(self):
        self.name = 'abstract'

    @abstractmethod
    def optimize(self, samples: DataFrame, metrics: Dict, attributes: List):
        pass
