import json

import inflect
import networkx as nx
import pandas as pd
from more_itertools import flatten
from itertools import combinations

from rapidfuzz import fuzz
from tqdm import tqdm

from entity.taxonomy import Taxonomy

hex_colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF', '#800000', '#008000', '#000080']

origin_to_color = {'cso': hex_colors[0], 'wikidata': hex_colors[1], 'gitranking': hex_colors[2]}

p = inflect.engine()


def normalize_word(word):
    tokens = word.replace('_', ' ').replace('-', ' ').split(' ')
    singulars = []
    for token in tokens:
        token = token.lower()
        t = p.singular_noun(token)
        normal = t if t else token
        singulars.append(normal)

    return ' '.join(singulars)


def build_joined_graph():
    taxonomies = ['cso', 'wikidata']

    all_terms = []
    for name in taxonomies:
        taxonomy = Taxonomy.load(f'../../data/interim/new_gitranking_{name}.json')
        all_terms.extend(flatten(taxonomy.pairs))

    # compair all combinations of terms in all_terms to check they fuzzy match, and create a new list of pairs and fuzzy
    # similarity score between them.
    all_terms = set(all_terms)
    combi = list(combinations(all_terms, 2))
    print(combi[:10])
    similarities = []
    for pair in tqdm(combi):
        t1 = normalize_word(pair[0])
        t2 = normalize_word(pair[1])

        sim = fuzz.ratio(t1, t2)
        similarities.append((pair[0], pair[1], sim, t1, t2))

    # Show the top 10 most similar pairs
    similarities.sort(key=lambda x: x[2], reverse=True)
    # filter out pairs with similarity score at 100
    same = [x for x in similarities if x[2] >= 97]

    # convert to mapping
    mapping = {}
    for pair in same:
        mapping[pair[0]] = pair[3]
        mapping[pair[1]] = pair[4]

    nodes = []
    for name in taxonomies:
        taxonomy = Taxonomy.load(f'../../data/interim/new_gitranking_{name}.json')
        for pair in taxonomy.pairs:
            source = mapping.get(pair[0], pair[0])
            target = mapping.get(pair[1], pair[1])
            nodes.append((source, target, name))

    wiki_nodes = [x for x in nodes if x[2] == 'wikidata']
    cso_nodes = [x for x in nodes if x[2] == 'cso']
    duplicates = [(x, y, 'both') for x, y, _ in wiki_nodes if (x, y, 'cso') in cso_nodes]
    nodes = [x for x in nodes if (x[0], x[1], 'both') not in duplicates]
    nodes.extend(duplicates)
    print(len(duplicates))

    nodes = [(x, y, origin_to_color[t]) for x, y, t in nodes]
    df = pd.DataFrame(nodes, columns=['source', 'target', 'color'])
    df.to_csv('../../data/interim/joined_graph.csv', index=False)
    nodes = [(x[0], x[1]) for x in nodes]
    g = nx.DiGraph()
    g.add_edges_from(nodes)
    print(g.number_of_nodes())
    print(g.number_of_edges())
    print(nx.is_directed_acyclic_graph(g))


if __name__ == '__main__':
    build_joined_graph()
