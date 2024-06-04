from typing import Any, Dict

import networkx
import networkx as nx
import numpy as np
from loguru import logger
from networkx import DiGraph

from entity import Taxonomy


class GraphMetrics:
    def __init__(self):
        self.columns_rename = {'nodes': '\# Nodes', 'edges': '\# Edges', 'roots': '\# Roots', 'leafs': '\# Leafs',
                               'parents': '\# Parents', 'max_parents': 'Max Parents', 'children': '\# Children',
                               'max_children': 'Max Children', 'bridges': '\# Bridges', 'inters': '\# Intermediate',
                               'num_self_loops': '\# Self Loops', 'num_cycles': '\# Cycles', 'CC': '\#  CC',
                               'DAG': 'Is DAG', 'new_terms': '\# New Terms', 'density': 'Density',
                               'avg_eccentricity': 'Avg Eccentricity',
                               'diameter': 'Diameter'}

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
        logger.info(f"Computing metrics for {graph}")
        metrics = self.simple_metrics(graph)
        metrics.update(self.taxonomy_metrics(taxonomy))
        metrics.update(self.connectivity_metrics(graph))
        metrics.update(self.structure_metrics(graph))
        return metrics

    @staticmethod
    def simple_metrics(graph: DiGraph) -> Dict[str, Any]:
        """
        Compute simple metrics for a graph. The metrics are:
        - Number of nodes
        - Number of edges
        - Number of roots
        - Number of leaves
        :param graph:
        :return:
        """
        logger.info(f"Computing simple metrics for {graph}")
        metrics = {'nodes': graph.number_of_nodes(),
                   'edges': graph.number_of_edges(),
                   'roots': len([x for x in graph.nodes() if graph.out_degree(x) == 0 and graph.in_degree(x) > 0]),
                   'leafs': len([x for x in graph.nodes() if graph.in_degree(x) == 0 and graph.out_degree(x) > 0]),
                   'density': nx.density(graph)}
        return metrics

    @staticmethod
    def connectivity_metrics(graph: DiGraph) -> Dict[str, Any]:
        """
        Compute connectivity metrics for a graph. The metrics are:
        - Avg, Std, and Max of the number parents
        - Avg, Std, and Max of the number children
        - Number of bridges
        - Number of intermediate nodes
        :param graph:
        :return:
        """
        logger.info(f"Computing connectivity metrics for {graph}")
        num_parents = [graph.out_degree(node) for node in graph.nodes()]
        num_children = [graph.in_degree(node) for node in graph.nodes()]
        k = networkx.strongly_connected_components(graph)
        eccentricity = []
        for c in k:
            g = graph.subgraph(c)
            ecc = list(nx.eccentricity(g).values())
            eccentricity.extend(ecc)
        avg_e = np.mean(eccentricity)
        diameter = max(eccentricity)
        metrics = {'parents': np.mean(num_parents),
                   'max_parents': np.max(num_parents),
                   'children': np.mean(num_children),
                   'max_children': np.max(num_children),
                   'bridges': len([x for x in graph.nodes() if graph.in_degree(x) == 1 and graph.out_degree(x) == 1]),
                   'inters': len([x for x in graph.nodes() if graph.in_degree(x) > 0 and graph.out_degree(x) > 0]),
                   'avg_eccentricity': avg_e,
                   'diameter': diameter,
                   }

        return metrics

    @staticmethod
    def structure_metrics(graph: DiGraph) -> Dict[str, Any]:
        """
        Compute structure metrics for a graph. The metrics are:
        - Number of self loops
        - Number of cycles
        - Number of connected components
        - Is Directed Acyclic Graph
        :param graph:
        :return:
        """
        logger.info(f"Computing structure metrics for {graph}")

        logger.info(f"Computing self loops")
        self_loops = len(list(nx.selfloop_edges(graph)))
        logger.info(f"Computing cycles")
        n_cycles = len(list(nx.simple_cycles(graph))) if graph.number_of_nodes() < 1000 else len(
            list(nx.simple_cycles(graph, length_bound=30)))
        logger.info(f"Computing number connected components")
        cc = nx.number_weakly_connected_components(graph)
        logger.info(f"Computing is DAG")
        is_dag = nx.is_directed_acyclic_graph(graph)

        metrics = {'num_self_loops': self_loops,
                   'num_cycles': n_cycles,
                   'CC': cc,
                   'DAG': is_dag
                   }

        return metrics

    def taxonomy_metrics(self, taxonomy):
        new_terms = len([x for x in taxonomy.terms if x not in taxonomy.gitranking_qid])
        metrics = {'new_terms': new_terms}
        return metrics
