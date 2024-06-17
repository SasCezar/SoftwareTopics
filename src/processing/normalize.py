from itertools import combinations

import numpy as np
from more_itertools import flatten
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from torchmetrics.functional import pairwise_cosine_similarity
from tqdm import tqdm

from entity.taxonomy import Taxonomy
from processing.processing import AbstractProcessing


class NormalizeTermsProcessing(AbstractProcessing):
    def __init__(self, embedding_model=None, threshold=0.95):
        self.embedding = SentenceTransformer(embedding_model)
        self.threshold = threshold

    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        taxonomy = self.normalize(taxonomy)
        taxonomy = taxonomy.update()
        return taxonomy

    def normalize(self, taxo: Taxonomy):
        """Compare all term pairs and decide whether they are the same or not"""
        terms = taxo.terms + list(taxo.gitranking_qid) + list(flatten(taxo.gitranking_aliases.values()))
        sim = self.semantic_compare(terms)
        sim = {(a, b): c for a, b, c in sim if c > self.threshold and a != b}
        dist = self.fuzzy_compare(terms)
        dist = {(a, b): c for a, b, c in dist if c > 95 and a != b}

        keys = set(dist.keys()).union(sim.keys())
        keys = [sorted(x, key=lambda x: len(x), reverse=True) for x in keys]
        keys = {x: y for x, y in keys}
        print(keys)
        print(len(keys))
        normalized_pairs = set()
        changed = {}
        inverted_git = {}

        for k, v in taxo.gitranking_aliases.items():
            for alias in v:
                inverted_git[alias] = k
        for src, dst, origin in taxo.pairs:

            if src in keys:
                changed[src] = keys[src]
                src_n = keys[src]

                if src_n in changed:
                    src_n = changed[src_n]

                src = src_n
            if src in inverted_git:
                src = inverted_git[src]
            if dst in keys:
                changed[dst] = keys[dst]
                dst_n = keys[dst]
                if dst_n in changed:
                    dst_n = changed[dst_n]
                dst = dst_n
            if dst in inverted_git:
                dst = inverted_git[dst]
            if src == dst:
                continue

            normalized_pairs.add((src, dst, origin))
        normalized_pairs = [list(x) for x in normalized_pairs]
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
        return sim

    @staticmethod
    def fuzzy_compare(terms):
        pairs = combinations(terms, 2)
        res = []
        for a, b in tqdm(pairs):
            score = fuzz.ratio(a, b)
            res.append((a, b, score))

        return res
