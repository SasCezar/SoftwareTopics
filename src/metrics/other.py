import copy
from pathlib import Path
from typing import Any, Dict

from networkx import DiGraph

from entity import Taxonomy
from processing import AbstractTermsRemovalProcessing


class OtherMetrics:
    def __init__(self, ranked_terms_path: Path):
        self.columns_rename = {'abstarct': '\# Abstract'}

        self.abstract = AbstractTermsRemovalProcessing(ranked_terms_path, 1)

    def metrics(self, graph: DiGraph, taxonomy: Taxonomy) -> Dict[str, Any]:
        """
        Compute metrics for a graph.

        Parameters
        ----------
        graph : networkx.DiGraph
            The graph to compute metrics for.

        taxonomy : Taxonomy
            The Taxonomy
        Returns
        -------
        dict
            A dictionary containing the computed metrics.
        """
        if 'num_removed' in taxonomy.post_process:
            return {'abstarct': taxonomy.post_process['num_removed']}
        t = self.abstract.process(taxonomy)
        num_abstract = t.post_process['num_removed']
        return {'abstarct': num_abstract}