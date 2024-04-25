import networkx as nx

from entity.taxonomy import Taxonomy
from processing.processing import AbstractProcessing


class BridgeRemovalProcessing(AbstractProcessing):
    def __init__(self):
        self.graph = nx.DiGraph()

    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        self.graph.add_edges_from([(a, b) for a, b, _ in taxonomy.pairs])
        name = taxonomy.name

        bridge_nodes = self.get_bridges(taxonomy)
        print(len(bridge_nodes))
        taxonomy.post_process['bridge_removed'] = bridge_nodes
        while bridge_nodes:
            for node in bridge_nodes:
                pred = list(self.graph.predecessors(node))[0]
                succ = list(self.graph.successors(node))[0]
                self.graph.remove_node(node)
                self.graph.add_edge(pred, succ)
                bridge_nodes = self.get_bridges(taxonomy)

        bridge_nodes = self.get_bridges(taxonomy)
        assert len(bridge_nodes) == 0
        pairs = list(self.graph.edges)
        taxonomy.pairs = [(a, b, name) for a, b in pairs]

        taxonomy = taxonomy.update()
        return taxonomy

    def get_bridges(self, taxonomy):
        return [node for node in self.graph.nodes
                if self.graph.in_degree(node) == 1
                and self.graph.out_degree(node) == 1
                and node not in taxonomy.gitranking_qid]
