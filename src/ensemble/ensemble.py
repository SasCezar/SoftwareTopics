from abc import ABC
from typing import List, Tuple

from entity import Taxonomy


class AbstractEnsemble(ABC):
    def complete(self, taxonomy_a: Taxonomy, taxonomy_b: Taxonomy) -> Taxonomy:
        pass

    @staticmethod
    def pairs2tuple(pairs: List[List[str]]) -> List[Tuple[str, str]]:
        return [(src, trg) for src, trg, _ in pairs]
