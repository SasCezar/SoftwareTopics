from pathlib import Path

import hydra
import pandas as pd
from hydra.utils import instantiate
from omegaconf import DictConfig
from tqdm import tqdm

from optimizer.optimizer import AbstractOptimizer


@hydra.main(version_base='1.3', config_path="../conf", config_name="optimize")
def rank(cfg: DictConfig):
    path = Path(cfg.taxonomy_folder)
    folders = [x for x in path.iterdir() if x.is_dir() and 'ensemble' not in str(x)]

    models_params = {'cso': ['LLM', 'Sim_Threshold'],
                     'LLM': ['LLM', 'prompt_type'],
                     'wikidata': ['Take_All', 'Types_Threshold', 'Max_Depth']}

    pp_og = ['cycle', 'bridge', 'abstract', 'minimization']
    exclude_pp = ['minimization']
    pp = [x for x in pp_og if x not in exclude_pp]

    optimizer: AbstractOptimizer = instantiate(cfg.optimizer)

    metrics = {c.metric: {'optimization': c.optimization, 'weight': c.weight} for c in cfg.metrics.metrics}
    for folder in tqdm(folders):
        metric_file = folder / 'melted_metrics.csv'
        name = folder.stem.split('_')[0]
        if '-' in name:
            name = name.split('-')[0]

        if not metric_file.exists():
            continue

        df = pd.read_csv(metric_file)

        attributes = models_params[name]
        print(metric_file.parent.stem)
        if 'processed' in metric_file.parent.stem:
            df.drop(columns=exclude_pp, inplace=True)
            attributes = models_params[name] + pp

        res = optimizer.optimize(df, metrics, attributes)

        res.to_csv(folder / f'ranked_models_{optimizer.name}_{cfg.metrics.name}.csv', index=False)
        res['Ranking'] = range(1, len(res) + 1)
        res = res[['Ranking'] + list(res.columns[:-1])]
        res.head(n=10).to_latex(folder / f'ranked_models_{optimizer.name}_{cfg.metrics.name}.tex', index=False,
                                float_format="{:.2f}".format)


if __name__ == '__main__':
    rank()
