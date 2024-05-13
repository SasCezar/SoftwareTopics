import networkx as nx
import numpy as np

from ensemble.ensemble import AbstractEnsemble
from entity import Taxonomy


class CascadeEnsemble(AbstractEnsemble):
    def complete(self, taxonomy_a: Taxonomy, taxonomy_b: Taxonomy) -> Taxonomy:
        missing_a = taxonomy_a.missing
        print(len(missing_a))
        print(len(set(missing_a).intersection(set(taxonomy_b.missing))))
        allowed = set(missing_a + taxonomy_a.terms)
        pairs_b = [(a, b) for a, b, _ in taxonomy_b.pairs]
        graph = nx.DiGraph()
        graph.add_edges_from(pairs_b)
        """Get all the paths starting from the missing terms to a root"""
        predecessors = {}
        for term in graph.nodes():
            predecessors[term] = list(nx.predecessor(graph, term))

        res = []
        for term in predecessors:
            terms = predecessors[term]
            for t in terms:
                paths = list(nx.all_simple_paths(graph, source=term, target=t))
                for path in paths:
                    inx = [i if t in allowed else 0 for i, t in enumerate(path)]
                    arg = np.argmax(inx)
                    path = path[:arg+1]
                    pairs = list(zip(path[:-1], path[1:], ['cascade']*len(path)))
                    res.extend(pairs)

        res = list(set(res))
        taxonomy_a.pairs.extend(res)
        taxonomy_a.update()
        print(len(set(missing_a).intersection(set(taxonomy_a.missing))))
        return taxonomy_a
