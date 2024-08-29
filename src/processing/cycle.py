from collections import defaultdict

import networkx as nx
import numpy as np
from loguru import logger

from entity.taxonomy import Taxonomy
from processing.processing import AbstractProcessing


class CycleRemovalProcessing(AbstractProcessing):
    def __init__(self):
        self.graph = nx.DiGraph()

    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        logger.info(f'Removing cycles')
        self.graph.add_edges_from([(a, b) for a, b, _ in taxonomy.pairs])
        self_loops = nx.selfloop_edges(self.graph)
        for loop in self_loops:
            self.graph.remove_edge(*loop)

        # Number of disjoint components
        components = list(nx.weakly_connected_components(self.graph))
        removed = []
        for component in components:
            subgraph = self.graph.subgraph(component).copy()
            try:
                dag = nx.is_directed_acyclic_graph(subgraph)
                if not dag:
                    down_links, subgraph = self.get_down_links(subgraph)
                    removed.extend(down_links)
                    assert nx.is_directed_acyclic_graph(subgraph)
            except nx.NetworkXNoCycle:
                pass

        logger.info(f"Number of components: {len(components)}")
        logger.info(f"Number of removed edges: {len(removed)}")
        for loop_edge in removed:
            self.graph.remove_edge(*loop_edge)
        assert nx.is_directed_acyclic_graph(self.graph)
        inverse_exists = [int(self.graph.has_edge(b, a)) for a, b in removed]
        percentage = sum(inverse_exists) / (len(inverse_exists)+1) * 100
        removed = [[a, b, z] for (a, b), z in zip(removed, inverse_exists)]
        taxonomy.post_process['cycle'] = removed
        taxonomy.post_process['percent_inverse'] = percentage
        taxonomy.pairs = [(a, b, name) for a, b, name in taxonomy.pairs if (a, b) in self.graph.edges]

        taxonomy = taxonomy.update()
        return taxonomy

    def distance(self, root, node):
        try:
            return nx.shortest_path_length(self.graph, node, root)
        except nx.NetworkXNoPath:
            return 0

    @staticmethod
    def get_down_links(graph: nx.DiGraph):
        roots = [node for node in graph.nodes if graph.out_degree(node) == 0 and graph.in_degree(node) > 0]

        logger.info(f"Roots: {len(roots)}")
        remove = []

        depth = defaultdict(int)
        for root in roots:
            d = nx.single_source_shortest_path_length(graph.reverse(), root)
            for k, v in d.items():
                depth[k] = max(depth[k], v)

        try:
            while cycle := nx.find_cycle(graph, orientation='reverse'):
                depth_difference = [depth[x] - depth[y] for x, y, _ in cycle]
                lowest = np.argmin(depth_difference)
                edge = cycle[lowest][:2]
                graph.remove_edge(*edge)
                remove.append(edge)
        except:
            pass

        return remove, graph
