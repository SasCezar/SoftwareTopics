from collections import defaultdict
from pathlib import Path

import numpy
from more_itertools import flatten
from rdflib import Graph
from sentence_transformers import SentenceTransformer
from torch.nn import CosineSimilarity
from tqdm import tqdm
from wikidata.client import Client

find_term_qids = """
                prefix owl: <http://www.w3.org/2002/07/owl#>   
                SELECT ?term ?id
                WHERE {{
                    ?term owl:sameAs ?id .
                }}
                """

normalize_query = """
                prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#>   
                SELECT ?s
                WHERE {{
                    <{term}> cso:preferentialEquivalent ?s .
                }}
        """

find_aliases = """
                prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#> 
                SELECT ?s
                WHERE {{
                    ?s cso:preferentialEquivalent <{term}> .
                }}
        """


def get_cso_terms(g):
    qres = list(g.query(find_term_qids))
    return {str(row[0]): str(row[1].split('/')[-1]) for row in qres if 'wikidata' in str(row[1])}


def get_aliases(graph, terms):
    aliases = defaultdict(list)
    for term in terms:
        res = [x[0] for x in graph.query(find_aliases.format(term=term))]
        res.append(term)
        aliases[term] = res

    return aliases


def get_normalized(graph, term):
    query = normalize_query.format(term=term)
    qres = list(graph.query(query))
    if qres:
        return qres[0][0]

    return term


client = Client()

model = SentenceTransformer('all-MiniLM-L6-v2')

from sklearn.metrics.pairwise import cosine_similarity

def get_similarities(syns, wiki_syns):
    syns = [model.encode(x) for x in syns]
    wiki_syns = [model.encode(x) for x in wiki_syns]

    similarities = cosine_similarity(syns, wiki_syns)
    print(similarities)
    similarities = list(flatten(similarities))
    return similarities


def correct_linked(terms, aliases):
    incorrect = defaultdict(int)
    correct = defaultdict(int)
    for term in tqdm(terms):
        q_id = terms[term]
        syns = aliases[term]
        wiki_term = client.get(q_id, load=True)
        try:
            wiki_syns = [x['value'] for x in wiki_term.data['aliases']['en']]
        except KeyError:
            wiki_syns = [wiki_term.label['en']]

        similarities = get_similarities(syns, wiki_syns)
        for threshold in numpy.arange(0, 1, 0.1):
            if any([x > threshold for x in similarities]):
                correct[threshold] += 1
            else:
                incorrect[threshold] += 1

    return correct, incorrect


def check_link_correctness():
    cso_path = Path('../../data/raw/CSO.3.3.nt')
    graph = Graph()
    graph.parse(str(cso_path), format='nt')
    terms = get_cso_terms(graph)
    aliases = get_aliases(graph, list(terms.keys()))
    correct_res, incorrect_res = correct_linked(terms, aliases)
    for threshold in numpy.arange(0, 1, 0.1):
        correct = correct_res[threshold]
        incorrect = incorrect_res[threshold]
        print(f'Correctness @ {threshold}: {correct / (correct + incorrect)}')
        print(f'Incorrectness @ {threshold}: {incorrect / (correct + incorrect)}')


if __name__ == '__main__':
    check_link_correctness()
