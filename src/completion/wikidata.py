import pandas as pd
from loguru import logger
from more_itertools import flatten
from tqdm import tqdm
from wikidata.client import Client

from completion.completion import AbstractCompletion
from entity.taxonomy import Taxonomy


class WikidataCompletion(AbstractCompletion):
    def __init__(self, take_all=False, types_path='', type_threshold=5, max_depth=2):
        self.wikidata = {}
        self.wikidata_qid = {}
        self.client = Client()
        self.type_threshold = type_threshold
        self.valid_types = self.load_types(types_path) if types_path else []
        self.name = f'wikidata'  # _ta_{take_all}_mo_{missing_only}_tt_{self.type_threshold}_md_{max_depth}'
        self.take_all = take_all
        self.seen_ancestors = {}
        self.max_depth = max_depth
        self.params = {'take_all': str(self.take_all),
                       'type_threshold': str(self.type_threshold),
                       'max_depth': str(self.max_depth)}

    def _parents(self, entity, depth):
        parents = []
        for parent in entity.data['claims'].get('P279', []):
            try:
                ancestor = self.client.get(parent['mainsnak']['datavalue']['value']['id'], load=True)
                ancestor_types = [x['mainsnak']['datavalue']['value']['id'] for x in
                                  ancestor.data['claims'].get('P31', [])]
                if (any(x in self.valid_types for x in ancestor_types) or self.take_all) or depth <= self.max_depth:
                    parents.append(ancestor)

            except KeyError:
                pass

        return parents

    def get_parents(self, qid):
        entity = self.client.get(qid, load=True)
        pairs = set()
        nodes = [(entity, 1)]
        while nodes:
            node, depth = nodes.pop()
            if node.id not in self.seen_ancestors:
                print(f'Depth {depth} for {node}')
                parents = self._parents(node, depth)
                self.seen_ancestors[node.id] = parents
                seen = False
            else:
                seen = True
                logger.info(f'Already seen {node}')
                parents = self.seen_ancestors[node.id]
            logger.info(f'Found {len(parents)} parents for {node}')
            if not seen:
                for parent in parents:
                    pairs.add((node, parent, self.name))
                    nodes.append((parent, depth + 1))

        return list(pairs)

    def complete(self, taxonomy: Taxonomy) -> Taxonomy:
        terms = list(taxonomy.terms)
        inverse_map = {q: k for k, q in taxonomy.gitranking_qid.items()}
        for term in tqdm(terms):
            logger.info(f'Processing {term}')
            pairs = self.get_parents(taxonomy.gitranking_qid[term])
            terms_qid = {x.label['en']: x.id for x in set(flatten([(x, y) for x, y, _ in pairs]))}
            pairs_name = [(inverse_map.get(x.id, x.label['en']), inverse_map.get(y.id, y.label['en']), t) for x, y, t in pairs]
            taxonomy.pairs.extend(pairs_name)
            taxonomy.wikidata_qid.update(terms_qid)

        taxonomy.update()
        taxonomy.other['params'] = self.params
        return taxonomy

    def load_types(self, path):
        df = pd.read_csv(path)
        types = df[df['count'] > self.type_threshold]['type'].tolist()
        return types
