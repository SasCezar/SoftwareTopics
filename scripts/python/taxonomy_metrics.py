import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from more_itertools import flatten
from tqdm import tqdm


def get_metrics(g):
    ## Add edge to root if not present
    # remove self loops
    metrics = {}
    num_self_loops  = len(list(nx.selfloop_edges(g)))
    g.remove_edges_from(nx.selfloop_edges(g))
    cc = list(nx.weakly_connected_components(g))
    cycles = [list(nx.simple_cycles(g.subgraph(x))) for x in cc if not nx.is_directed_acyclic_graph(g.subgraph(x))]
    cycles = [len(x) for x in cycles if len(x) > 0]
    metrics.update({'roots': len([x for x in g.nodes() if g.out_degree(x) == 0 and g.in_degree(x) > 0]),
               'leafs': len([x for x in g.nodes() if g.in_degree(x) == 0 and g.out_degree(x) > 0]),
               'nodes': g.number_of_nodes(),
               'edges': g.number_of_edges(),
               'cc': nx.number_weakly_connected_components(g),
               'num_dag_cc': sum([1 for x in nx.weakly_connected_components(g) if nx.is_directed_acyclic_graph(g.subgraph(x))]),
               'num_cycles': len(cycles),
               'cycle_size': int(np.mean(cycles)) if len(cycles) > 0 else 0,
                'num_self_loops': num_self_loops
               })
    # g.add_node('unconnected')
    # for node in g.nodes():
    #     if g.in_degree(node) == 0 and g.out_degree(node) == 0:
    #         g.add_edge('unconnected', node)
    # metrics["forest"] = str(nx.is_forest(g))[0]
    metrics["DAG"] = str(nx.is_directed_acyclic_graph(g))[0]
    intermediate_nodes = [x for x in g.nodes() if g.in_degree(x) > 0 and g.out_degree(x) > 0]
    metrics['inters'] = len(intermediate_nodes)
    bridge_nodes = [x for x in g.nodes() if g.in_degree(x) == 1 and g.out_degree(x) == 1]
    metrics['bridges'] = len(bridge_nodes)

    return metrics


def fix_params(param):
    if isinstance(param, list):
        if len(param) == 4:
            return {'ta': str(param[0])[0], 'mo': str(param[1])[0],
                    'tt': param[2], 'md': param[3]}
        if len(param) == 2:
            return {'LLM': param[0], 'sim_t': param[1]}

    return param


def measure_taxonomies():
    path = Path('../../data/interim/taxonomy')
    folders = list(path.iterdir())
    all_pairs = {}
    graphs = {}
    llm_pred = pd.read_csv('/pipeline/pairs_llm_results.csv')
    llm_pred = llm_pred.set_index(['term', 'parent']).to_dict()['pred']
    for folder in folders:
        files = [x for x in folder.iterdir() if x.suffix == '.json']
        metrics = []
        for file in tqdm(files, desc=folder.stem):
            with open(file, 'r') as f:
                taxonomy = json.load(f)
                pairs = [(x[0], x[1]) for x in taxonomy['pairs']]
                all_pairs[file.stem] = pairs
                llm_pair_pred = [llm_pred.get((x[0], x[1]), 0) for x in pairs]
                acc = np.mean(llm_pair_pred)
                g = nx.DiGraph()
                g.add_edges_from(pairs)
                r = {}
                r.update(fix_params(taxonomy['other']['params']))
                r.update(get_metrics(g))
                r.update({'unlk': len(set(taxonomy['terms']) - set(flatten(pairs)))})
                r.update({'acc': acc})
                metrics.append(r)
                graphs[file.stem] = g

        df = pd.DataFrame(metrics)
        df = df.sort_values(by=['take_all', 'type_threshold', 'max_depth']) if 'take_all' in df.columns else df.sort_values(by=['llm', 'sim_t'])
        df.to_csv(folder / 'metrics.csv', index=False)
        df.to_latex(folder / 'metrics.tex', index=False, escape=True, float_format="{:.2f}".format)


if __name__ == '__main__':
    measure_taxonomies()
