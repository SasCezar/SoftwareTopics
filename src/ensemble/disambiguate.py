from itertools import combinations

import numpy as np
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from torchmetrics.functional import pairwise_cosine_similarity
from tqdm import tqdm

from ensemble.simple import SimpleEnsemble
from entity import Taxonomy


class DisambiguateEnsemble(SimpleEnsemble):
    def __init__(self, embedding_model=None, threshold=0.9):
        super().__init__()
        self.embedding = SentenceTransformer(embedding_model)
        self.threshold = threshold

    def complete(self, taxonomy_a: Taxonomy, taxonomy_b: Taxonomy) -> Taxonomy:
        taxo = super().complete(taxonomy_a, taxonomy_b)
        taxo = self.disambiguate(taxo)
        taxo.update()
        return taxo

    def disambiguate(self, taxo: Taxonomy):
        """Compare all term pairs and decide whether they are the same or not"""
        sim = self.semantic_compare(taxo.terms)
        sim = {(a, b): c for a, b, c in sim if c > self.threshold}
        dist = self.fuzzy_compare(taxo.terms)
        dist = {(a, b): c for a, b, c in dist if c > 85}

        keys = set(dist.keys()).intersection(sim.keys())

        keys = [sorted(x, key=lambda x: len(x), reverse=True) for x in keys]
        keys = {x:y for x,y in keys}
        normalized_pairs = []
        for src, dst, origin in taxo.pairs:
            src = keys.get(src, src)
            dst = keys.get(dst, dst)
            normalized_pairs.append([src, dst, origin]) if [src, dst, origin] not in normalized_pairs else None
        taxo.pairs = normalized_pairs
        return taxo

    def semantic_compare(self, terms):
        emb = self.embedding.encode(terms, convert_to_numpy=False, convert_to_tensor=True)
        sim = pairwise_cosine_similarity(emb).numpy()
        """Set lower triangle to 0"""
        sim[np.tril_indices(sim.shape[0], -1)] = 0
        """Get the indices of the pairs that are similar"""
        sim_ix = np.argwhere(sim > self.threshold)
        sim = [(terms[i], terms[j], sim[i, j]) for i, j in sim_ix]
        sim = sorted(sim, key=lambda x: x[2], reverse=True)
        print(sim)
        print(len(sim))
        return sim

    @staticmethod
    def fuzzy_compare(terms):
        pairs = combinations(terms, 2)
        res = []
        for a, b in tqdm(pairs):
            score = fuzz.ratio(a, b)
            res.append((a, b, score))

        return res
