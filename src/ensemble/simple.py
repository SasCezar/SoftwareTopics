from ensemble.ensemble import AbstractEnsemble
from entity import Taxonomy


class Simple(AbstractEnsemble):
    def complete(self, taxonomy_a: Taxonomy, taxonomy_b: Taxonomy) -> Taxonomy:
        pairs_a = taxonomy_a.pairs
        pairs_b = taxonomy_b.pairs
        res = Taxonomy()
        intersection = set(self.pairs2tuple(pairs_a)).intersection(set(self.pairs2tuple(pairs_b)))
        inter_pairs = [(src, trg, 'both') for src, trg in intersection]
        pairs_a = [x for x in pairs_a if (x[0], x[1]) not in intersection]
        pairs_b = [x for x in pairs_b if (x[0], x[1]) not in intersection]

        # We combine all the info from both taxonomies, regardless of whether they are present in both or not
        res.pairs = pairs_a + inter_pairs + pairs_b
        res.gitranking_qid = taxonomy_a.gitranking_qid
        res.gitranking_aliases = taxonomy_a.gitranking_aliases

        res.cso_mapping = taxonomy_a.cso_mapping
        res.cso_mapping.update(taxonomy_b.cso_mapping)
        res.cso_qid = taxonomy_a.cso_qid
        res.cso_qid.update(taxonomy_b.cso_qid)

        res.wikidata_qid = taxonomy_a.wikidata_qid
        res.wikidata_qid.update(taxonomy_b.wikidata_qid)
        res.other['params_a'] = taxonomy_a.other['params']
        res.other['params_b'] = taxonomy_b.other['params']

        return res
