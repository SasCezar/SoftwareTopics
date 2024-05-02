from pathlib import Path

import hydra
import networkx as nx
import pandas as pd
from loguru import logger
from omegaconf import DictConfig
from tqdm import tqdm

from entity import Taxonomy
from metrics import GraphMetrics, SemanticMetrics


def format_params(param):
    res = {}
    params_maps = {'take_all': 'Take All', 'type_threshold': 'Types Threshold',
                   'max_depth': 'Max Depth', 'llm': 'LLM', 'sim_t': 'Sim Threshold'}
    for key, value in param.items():
        if key in params_maps:
            if key == 'take_all':
                value = str(value)[0]
            if key == 'type_threshold':
                value = int(value)
            res[params_maps[key]] = value
        else:
            res[key] = value
    return res


@hydra.main(version_base='1.3', config_path="../conf", config_name="complete_taxonomy")
def compute_metrics(cfg: DictConfig):
    path = Path(cfg.taxonomy_folder)
    folders = [x for x in path.iterdir() if x.is_dir()]
    pairs_pred_path = f'{cfg.data}/result/pairs_llm_results.csv'
    eval_functions = [GraphMetrics(), SemanticMetrics(pairs_pred_path=pairs_pred_path)]
    metrics_rename = {}
    taxo_stats = {'num_unique_missing': 'Missing'}
    for function in eval_functions:
        metrics_rename.update(function.columns_rename)

    for folder in folders:
        files = [x for x in folder.iterdir() if x.suffix == '.json']
        metrics = []
        for file in tqdm(files, desc=folder.stem):
            pp = {'cycle': 0, 'bridge': 0, 'abstract': 0, 'minimization': 0}

            taxonomy = Taxonomy.load(file)
            taxonomy = taxonomy.update()
            pairs = [(x[0], x[1]) for x in taxonomy.pairs]
            g = nx.DiGraph()
            g.add_edges_from(pairs)
            row = format_params(taxonomy.other['params'])
            logger.info(f"Processing {file.stem}")
            if 'processed' in folder.stem:
                pp.update(taxonomy.other['post_processing'])
                pp = {x: str(y) for x, y in pp.items()}
                row.update(pp)
                row.update()
            for function in eval_functions:
                logger.info(f"Processing {function}")
                row.update(function.metrics(g))
            for stat, map in taxo_stats.items():
                row.update({map: taxonomy.dict()[stat]})
                metrics_rename.update({map: map})
            metrics.append(row)

        df = pd.DataFrame(metrics)
        df.sort_values(by=list(format_params(taxonomy.other['params']).keys()), ascending=True, inplace=True)

        if 'Sim Threshold' in df.columns:
            df['Sim Threshold'] = df['Sim Threshold'].astype(float)
            df['Sim Threshold'] = df['Sim Threshold'].replace(2,
                                                              1)  # When running, to avoid errors do to float precision we used 2 as threshold as 1 might not be exactly 1. We replace this in output

        if 'Take All' in df.columns:
            """Replace the value if take all is True"""
            df.loc[df['Take All'] == 'T', 'Max Depth'] = "NA"
            df.loc[df['Take All'] == 'T', 'Types Threshold'] = "NA"

        if 'processed' in folder.stem:
            df.fillna('-', inplace=True)
            pp_names = list(pp.keys())
        else:
            pp_names = []

        df.rename(columns=metrics_rename, inplace=True)
        df.to_csv(folder / 'metrics.csv', index=False)

        metrics_name = [x for x in metrics_rename.values() if x in df.columns]
        header_order = list(format_params(taxonomy.other['params']).keys()) + pp_names + metrics_name
        df.sort_values(by=list(format_params(taxonomy.other['params']).keys()) + pp_names, ascending=True,
                       inplace=True)

        df = df[header_order]
        df.to_latex(folder / 'metrics.tex', index=False,
                    escape=False, float_format="{:.2f}".format,
                    header=['\\rot{{' + x + '}}' for x in df.columns])

        id_vars = list(format_params(taxonomy.other['params']).keys()) + pp_names
        header_rename = {x: str(x).replace(" ", "_") for x in id_vars}
        df.rename(columns=header_rename, inplace=True)

        melted = df.melt(id_vars=header_rename.values(),
                         value_vars=metrics_name,
                         var_name='Metric', value_name='Value')
        melted.to_csv(folder / 'melted_metrics.csv', index=False)
        df = melted
        if not 'processed' in folder.stem:
            continue
        df['post_process_list'] = df[pp_names].values.tolist()
        df['pp_name'] = df['post_process_list'].apply(
            lambda x: "_".join([pp_names[i] for i, k in enumerate(x) if bool(int(k))]))
        df['num_pp'] = df[pp_names].astype(int).sum(axis=1)
        df.drop(df[df['num_pp'] > 1].index, inplace=True)
        df['is_pp'] = df['num_pp'] > 0
        df.drop(columns=pp_names, inplace=True)
        df.drop(columns=['num_pp', 'post_process_list'], inplace=True)
        res = [df]
        for pp in pp_names:
            no_pp = df[df['is_pp'] == 0].copy(deep=True)
            no_pp['pp_name'] = pp
            res.append(no_pp)
        df.drop(df[df['pp_name'] == ''].index, inplace=True)
        df = pd.concat(res)
        df.to_csv(folder / 'extra_melted_metrics.csv', index=False)


if __name__ == '__main__':
    compute_metrics()
