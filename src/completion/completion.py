from abc import ABC

from entity.taxonomy import Taxonomy


class AbstractCompletion(ABC):
    def complete(self, taxonomy: Taxonomy) -> Taxonomy:
        pass
