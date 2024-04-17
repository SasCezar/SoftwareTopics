import json
from pathlib import Path

import networkx as nx
import pandas as pd
from pyvis.network import Network
from rdflib import Graph
from tqdm import tqdm

parent_query = """
        prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#>   
        SELECT ?s
        WHERE {{
            ?s cso:superTopicOf <{hyponym}> .
        }}"""

normalize_query = """
        prefix cso: <http://cso.kmi.open.ac.uk/schema/cso#>   
        SELECT ?s
        WHERE {{
            <{term}> cso:preferentialEquivalent ?s .
        }}
"""

wikidata_id_query = """
        prefix owl: <http://www.w3.org/2002/07/owl#>   
        SELECT ?s
        WHERE {{
            ?s owl:sameAs <http://www.wikidata.org/entity/{qid}> .
        }}
"""


def build_joined(graph_path, terms):
    g = Graph()
    g.parse(graph_path)
    res = []
    unmatched_terms = set()

    for term in tqdm(terms):
        # recursively get all the parents of the term
        nodes = [f'https://cso.kmi.open.ac.uk/topics/{term.replace(" ", "_")}']
        matched = False
        while nodes:
            term = nodes.pop()
            qres = list(g.query(parent_query.format(hyponym=term)))
            for row in qres:
                if row:
                    parent = row[0]
                    res.append((term, parent))
                    nodes.append(row[0])
                    matched = True
        if not matched:
            unmatched_terms.add(term)

    return res, unmatched_terms


def load_gitranking_taxonomy(gitranking_path):
    terms_title = {}
    with open(gitranking_path) as f:
        for line in f:
            term = json.loads(line)
            # terms_qid[term['id']] = term['Wikidata ID']
            terms_title[term['Wikidata Title']] = term['Wikidata ID']

    return terms_title


def build_graph(pairs):
    edges = []
    for pair in pairs:
        edges.append((str(pair[0]), str(pair[1])))

    taxo = nx.DiGraph()
    for edge in edges:
        taxo.add_edge(edge[0], edge[1])
    return taxo


def _normal(g, param):
    qres = list(g.query(normalize_query.format(term=param)))
    if qres:
        return qres[0][0]
    else:
        return param


def normalize_single(graph_path, res):
    seen = {}
    normalized = []
    g = Graph()
    g.parse(graph_path)
    for n in tqdm(res):
        if n not in seen:
            seen[n] = _normal(g, f"https://cso.kmi.open.ac.uk/topics/{n}")

        normalized.append(seen[n].replace("https://cso.kmi.open.ac.uk/topics/", ""))

    #fix encoding issues with url, %28 an %29 are ( and ) respectively
    normalized = [x.replace("%28", "(").replace("%29", ")") for x in normalized]
    return normalized

def normalize(graph_path, res):
    seen = {}
    normalized = []
    g = Graph()
    g.parse(graph_path)
    for n in tqdm(res):
        if n[0] not in seen:
            seen[n[0]] = _normal(g, n[0])

        if n[1] not in seen:
            seen[n[1]] = _normal(g, n[1])

        normalized.append((seen[n[0]].replace("https://cso.kmi.open.ac.uk/topics/", ""),
                           seen[n[1]].replace("https://cso.kmi.open.ac.uk/topics/", "")))

    #fix encoding issues with url, %28 an %29 are ( and ) respectively
    normalized = [(x[0].replace("%28", "(").replace("%29", ")"), x[1].replace("%28", "(").replace("%29", ")")) for x in normalized]
    return normalized


def map_qids(graph_path, q_ids):
    g = Graph()
    g.parse(graph_path)

    mapped_qids = []
    for qid in tqdm(q_ids):
        qres = list(g.query(wikidata_id_query.format(qid=qid)))
        if qres:
            mapped_qids.append(qres[0][0].replace("https://cso.kmi.open.ac.uk/topics/", ""))
        else:
            mapped_qids.append(None)

    return mapped_qids


if __name__ == '__main__':
    cso_path = Path('../../data/raw/CSO.3.3.nt')
    gitranking_path = Path('../../data/raw/gitranking.jsonl')
    gitranking_taxonomy_title = load_gitranking_taxonomy(gitranking_path)
    #keys = [x.lower().replace(' ', '_') for x in gitranking_taxonomy_title.keys()]
    titles = [x.lower().replace(' ', '_') for x in gitranking_taxonomy_title.keys()]
    q_ids = [gitranking_taxonomy_title[x] for x in gitranking_taxonomy_title]
    mapped_qids = map_qids(cso_path, q_ids)

    keys = []
    for qid, mapped, title in zip(q_ids, mapped_qids, titles):
       if mapped:
           keys.append(mapped)
       else:
           keys.append(title)

    keys = normalize_single(cso_path, keys)
    res, unmatched = build_joined(cso_path, keys)
    normalized = list(set(normalize(cso_path, res)))
    df = pd.DataFrame(normalized, columns=['hypernym', 'hyponym'])
    df.to_csv('../../data/interim/gitranking_cso.csv', index=False)
    taxo = build_graph(normalized)
    taxo.add_node('root')
    # create a root node for the graph and add all nodes that have no parents
    intermediate_nodes = []
    multiple_parents = []
    multiple_children = []
    for node in taxo.nodes:
        ## if the node has no parents add it to the root
        if not taxo.out_edges(node) and node != 'root':
            taxo.add_edge(node, 'root')
        if len(taxo.in_edges(node)) == 1 and len(taxo.out_edges(node)) == 1:
            intermediate_nodes.append(node)
        if len(taxo.out_edges(node)) > 1:
            multiple_parents.append(node)
        if len(taxo.in_edges(node)) > 1:
            multiple_children.append(node)
    print('Total Nodes', taxo.number_of_nodes())
    print('Intermediate nodes', len(intermediate_nodes))
    print('Multiple parent', len(multiple_parents))
    print('Multiple children', len(multiple_children))
    nx.write_graphml(taxo, '../../data/interim/gitranking_cso.graphml')
    nt = Network(width='100%', filter_menu=True)
    nt.show_buttons(filter_=['physics'])
    nt.from_nx(taxo)
    print("Unmatched", len(unmatched))
    print(unmatched)
    unmatched_df = pd.DataFrame(unmatched, columns=['unmatched'])
    unmatched_df.to_csv('../../data/interim/gitranking_cso_unmatched.csv', index=False)
    #nt.show('pyvis_taxo.html', notebook=False)
    is_acyclic = nx.is_directed_acyclic_graph(taxo)
    print('Is acyclic', is_acyclic)
    print('Is tree', nx.is_tree(taxo))