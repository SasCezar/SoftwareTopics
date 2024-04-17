import pandas as pd
from more_itertools import flatten

from entity.taxonomy import Taxonomy
from pipeline.find_equivalent import normalize_word

hex_colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF', '#FF00FF', '#800000', '#008000', '#000080']

origin_to_color = {'cso': hex_colors[0], 'wikidata': hex_colors[1], 'both': hex_colors[2]}


def build_joined_graph():
    taxonomies = ['cso', 'wikidata']

    nodes = []
    cso_qid = set()
    wikidata_qid = set()
    inverted_wiki_qid = {}
    inverted_cso_qid = {}
    for name in taxonomies:
        taxonomy = Taxonomy.load(f'../../data/interim/new_gitranking_{name}.json')
        nodes.extend(taxonomy.pairs)
        cso_qid.update(taxonomy.cso_qid.values())
        wikidata_qid.update(taxonomy.wikidata_qid.values())
        inverted_wiki_qid.update({v: k for k, v in taxonomy.wikidata_qid.items()})
        inverted_cso_qid.update({v: k for k, v in taxonomy.cso_qid.items()})

    wiki_nodes = set(flatten([x for x in nodes if x[2] == 'wikidata']))
    cso_nodes = set(flatten([x for x in nodes if x[2] == 'cso']))
    intersection = wiki_nodes.intersection(cso_nodes)
    print(len(intersection))
    nodes = [(x, y, origin_to_color[t]) for x, y, t in nodes]
    df = pd.DataFrame(nodes, columns=['source', 'target', 'color'])
    df.to_csv('../../data/interim/joined_graph.csv', index=False)
    qid_intersection = cso_qid.intersection(wikidata_qid)
    print(len(qid_intersection))
    wrong_match = []
    for qid in qid_intersection:
        if normalize_word(inverted_cso_qid[qid]) != normalize_word(inverted_wiki_qid[qid]):
            wrong_match.append((inverted_cso_qid[qid], inverted_wiki_qid[qid], qid))

    print(wrong_match)


if __name__ == '__main__':
    build_joined_graph()
