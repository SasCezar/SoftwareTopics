from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from networkx import DiGraph


class SemanticMetrics:
    def __init__(self, pairs_pred_path: str, ad_pred_path: Optional[str] = None):
        self.pred_pairs = pd.read_csv(pairs_pred_path)
        self.pred_pairs = self.pred_pairs.set_index(['term', 'parent']).to_dict()['pred']
        self.pred_ad = pd.read_csv(ad_pred_path) if ad_pred_path else None
        self.columns_rename = {'edge_accuracy': 'Pairs Acc', 'node_accuracy': 'AD Acc'}

    def metrics(self, graph: DiGraph) -> Dict[str, Any]:
        """
        Compute semantic metrics for a graph. Semantic metrics are based on the edges of the graph.

        Parameters:
        ----------
        graph : networkx.DiGraph
            The graph to compute metrics for.

        Returns
        -------
        dict
            A dictionary containing the computed metrics.
        """
        pairs = [(a, b) for a, b in graph.edges()]
        metrics = self.edge_metrics(pairs)
        metrics.update(self.node_metrics(list(graph.nodes))) if self.pred_ad else None
        return metrics

    def edge_metrics(self, pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        llm_pair_pred = [self.pred_pairs.get((x[0], x[1]), 0) for x in pairs]
        acc = np.mean(llm_pair_pred)
        return {'edge_accuracy': acc}

    def node_metrics(self, nodes: List[str]) -> Dict[str, Any]:
        llm_node_pred = [self.pred_ad.get(x, 0) for x in nodes]
        acc = np.mean(llm_node_pred)
        return {'node_accuracy': acc}
