import json
from typing import List, Dict

from more_itertools import flatten
from pydantic import BaseModel


class Taxonomy(BaseModel):
    terms: List = []
    pairs: List = []
    missing: List = []
    name: str = ''
    gitranking_qid: Dict = {}
    cso_qid: Dict = {}
    cso_mapping: Dict = {}
    cso_normalized: Dict = {}
    wikidata_qid: Dict = {}
    gitranking_aliases: Dict = {}
    other: Dict = {}
    post_process: Dict = {}
    num_terms: int = 0
    num_pairs: int = 0
    num_missing: int = 0
    num_unique_terms: int = 0
    num_unique_pairs: int = 0
    num_unique_missing: int = 0

    @staticmethod
    def compute_stats(taxonomy):
        taxonomy.num_terms = len(taxonomy.terms)
        taxonomy.num_pairs = len(taxonomy.pairs)
        taxonomy.num_missing = len(taxonomy.missing)
        taxonomy.num_unique_terms = len(set(taxonomy.terms) | set(flatten(taxonomy.pairs)))
        taxonomy.num_unique_pairs = len(set([tuple(x) for x in taxonomy.pairs]))
        taxonomy.num_unique_missing = len(set(taxonomy.missing))
        return taxonomy

    def update(self):
        self.terms = list(set(flatten([x[:2] for x in self.pairs])))
        self.missing = list(set(self.gitranking_qid.keys()) - set(self.terms))
        return Taxonomy.compute_stats(self)

    @staticmethod
    def load(path):
        with open(path) as f:
            obj = json.load(f)
            return Taxonomy(**obj)