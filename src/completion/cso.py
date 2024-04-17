import numpy as np
from more_itertools import flatten
from rdflib import Graph
from sentence_transformers import SentenceTransformer
from torch.nn import CosineSimilarity
from tqdm import tqdm

from completion.completion import AbstractCompletion
from entity.taxonomy import Taxonomy


class CSOCompletion(AbstractCompletion):
    def __init__(self, cso_path, sentence_transformer='all-mpnet-base-v2', threshold=0.5):
        self.cso_path = cso_path
        self.graph = Graph()
        self.name = f'cso'  # _st_{sentence_transformer}_th_{threshold}'
        self.sentence_transformer = sentence_transformer
        self.threshold = threshold
        self.graph.parse(cso_path)
        self.topics = self.load_topics(cso_path)
        self.embedding = SentenceTransformer(sentence_transformer)
        self.cos = CosineSimilarity()
        self.params = {'llm': self.sentence_transformer, 'sim_t': str(self.threshold)}

        self.parent_query = """
                prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#>   
                SELECT ?s
                WHERE {{
                    ?s cso:superTopicOf <{hyponym}> .
                }}
        """

        self.normalize_query = """
                prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#>   
                SELECT ?s
                WHERE {{
                    <{term}> cso:preferentialEquivalent ?s .
                }}
        """

        self.find_by_qid_query = """
                prefix owl: <http://www.w3.org/2002/07/owl#>   
                SELECT ?s
                WHERE {{
                    ?s owl:sameAs <http://www.wikidata.org/entity/{qid}> .
                }}
        """

        self.find_qid_query = """
                prefix owl: <http://www.w3.org/2002/07/owl#>   
                SELECT ?id
                WHERE {{
                    <{term}> owl:sameAs ?id .
                }}
        """

        self.alias_query = """
                prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#> 
                SELECT ?s
                WHERE {{
                    ?s cso:preferentialEquivalent <{term}> .
                }}
        """

        self.mapping = {}
        self.inverse_mapping = {}
        self.mapping_qid = {}
        self.normalized = {}

        self.wrong_match = 0

    def get_parents(self, term):
        term = self.format_term(term)
        query = self.parent_query.format(hyponym=term)
        qres = list(self.graph.query(query))
        return [row[0] for row in qres]

    def ancestors_pairs(self, term):
        term = self.format_term(term)
        nodes = [term]
        parents = []
        seen = set()
        while nodes:
            term = nodes.pop()
            if term in seen:
                continue
            _parents = self.get_parents(term)
            for p in _parents:
                parents.append((term, p))
                nodes.extend(_parents)
            seen.add(term)

        return parents

    def find_by_qid(self, qid):
        query = self.find_by_qid_query.format(qid=qid)
        qres = list(self.graph.query(query))
        if qres:
            return qres[0][0]
        return None

    def get_normalized(self, term):
        term = self.format_term(term)
        query = self.normalize_query.format(term=term)
        qres = list(self.graph.query(query))
        if qres:
            self.normalized[term] = qres[0][0]
            return qres[0][0]

        self.normalized[term] = None
        return term

    def get_aliases(self, term):
        query = self.alias_query.format(term=term)
        qres = list(self.graph.query(query))
        return [row[0] for row in qres] + [term]

    def find_qid(self, term):
        term = self.format_term(term)
        query = self.find_qid_query.format(term=term)
        qres = list(self.graph.query(query))
        if qres:
            for row in qres:
                if 'wikidata' in row[0]:
                    return row[0].split('/')[-1].replace('>', '')

        return None

    def find_term(self, term, qid=None, term_alias=None):
        if term_alias is None:
            term_alias = []
        term = term.replace(" ", "_")
        terms = [t.replace(" ", "_").lower() for t in term_alias] + [term]
        terms = list(set(terms))
        print("Terms", terms)

        matched_qids = []
        matched_terms = []

        if qid:
            matched = self.find_by_qid(qid)
            if matched:
                aliases = self.get_aliases(self.get_normalized(matched))
                sims = [self.similarity(matched_term_a, term_aliases)
                        for matched_term_a in aliases for term_aliases in terms]
                if sims and np.max(sims) > self.threshold:
                    self.mapping[self.clean(term)] = self.get_normalized(matched)
                    self.inverse_mapping[self.clean(self.get_normalized(matched))] = self.clean(term)
                    self.mapping_qid[self.clean(term)] = qid
                    return self.mapping[self.clean(term)]

        for t in terms:
            found_qid = self.find_qid(t)
            matched_qids.append(found_qid)
            matched_terms.append(self.find_by_qid(found_qid))

        for t, q in zip(matched_terms, matched_qids):
            if q == qid:
                self.mapping[self.clean(term)] = self.get_normalized(t)
                self.inverse_mapping[self.clean(self.get_normalized(t))] = self.clean(term)
                self.mapping_qid[self.clean(term)] = q
                return self.mapping[self.clean(term)]

            aliases = self.get_aliases(self.get_normalized(t))
            parents = self.get_parents(self.get_normalized(t))
            p_aliases = list(flatten([self.get_aliases(x) for x in parents]))
            related = list(set(aliases + parents + p_aliases))
            sims = [self.similarity(matched_term_a, term_aliases) for matched_term_a in related
                    for term_aliases in terms]
            if sims and np.max(sims) > self.threshold:
                self.mapping[self.clean(term)] = self.get_normalized(t)
                self.inverse_mapping[self.clean(self.get_normalized(t))] = self.clean(term)
                self.mapping_qid[self.clean(term)] = q
                return self.mapping[self.clean(term)]

        return None

    def complete(self, taxonomy: Taxonomy) -> Taxonomy:
        terms = list(taxonomy.terms)
        for term in tqdm(terms):
            print('Analyzing', term)
            normalized_term = self.find_term(term, taxonomy.gitranking_qid[term], taxonomy.gitranking_aliases[term])
            if normalized_term:
                pairs = self.ancestors_pairs(normalized_term)
                normalized_pairs = {(self.get_normalized(x), self.get_normalized(y)) for x, y in pairs}
                pairs = [(self.clean(x), self.clean(y)) for x, y in normalized_pairs]
                pairs = [(self.inverse_mapping.get(x, x), self.inverse_mapping.get(y, y), 'cso') for x, y in pairs]
                taxonomy.pairs.extend(pairs)

        taxonomy.cso_mapping = self.mapping
        taxonomy.cso_qid = self.mapping_qid
        taxonomy.pairs = list(set(taxonomy.pairs))
        taxonomy.cso_normalized = self.normalized
        taxonomy.other = {'wrong_match': self.wrong_match, 'params': self.params}
        taxonomy.update()

        return taxonomy

    @staticmethod
    def clean(term):
        return term.replace("https://cso.kmi.open.ac.uk/topics/", "").replace("_", " ")

    @staticmethod
    def format_term(term):
        if term is None:
            return None
        if term.startswith('http'):
            return term
        return f"https://cso.kmi.open.ac.uk/topics/{term.replace(' ', '_')}"

    def similarity(self, term1, term2):
        if not term1 or not term2:
            return 0
        t1 = self.clean(term1)
        t2 = self.clean(term2)
        emb = self.embedding.encode([t1, t2], convert_to_numpy=False, convert_to_tensor=True)
        sim = self.cos(emb[0].reshape(1, -1), emb[1].reshape(1, -1))
        return sim[0].item()

    def load_topics(self, cso_path):
        topics = set()
        with open(cso_path, 'r') as f:
            for line in f:
                elements = line.split(' ')
                for e in elements:
                    if e.startswith("<https://cso.kmi.open.ac.uk/topics/"):
                        topics.add(e.replace("<", "").replace(">", ""))
        return topics
