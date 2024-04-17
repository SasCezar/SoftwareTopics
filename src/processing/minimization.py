from more_itertools import flatten
from networkx import DiGraph

from entity.taxonomy import Taxonomy
from processing.processing import AbstractProcessing


class ExtraTermRemovalProcessing(AbstractProcessing):
    def __init__(self):
        self.graph = DiGraph()

    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        self.graph.add_edges_from([(a, b) for a, b, _ in taxonomy.pairs])
        nodes = list(self.graph.nodes)

        for node in nodes:
            if node not in taxonomy.gitranking_qid:
                predecessors = list(self.graph.predecessors(node))
                successors = list(self.graph.successors(node))

                for predecessor in predecessors:
                    for successor in successors:
                        self.graph.add_edge(predecessor, successor)

                self.graph.remove_node(node)

        src = taxonomy.pairs[0][0]
        taxonomy.pairs = [(a, b, src) for a, b in self.graph.edges]
        taxonomy.terms = list(set(flatten(taxonomy.pairs)))

        return taxonomy
