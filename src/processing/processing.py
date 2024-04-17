from abc import ABC

from entity.taxonomy import Taxonomy


class AbstractProcessing(ABC):
    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        raise NotImplementedError
