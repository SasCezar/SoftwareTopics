from pathlib import Path

import hydra
import pandas as pd
from omegaconf import DictConfig


@hydra.main(version_base='1.3', config_path="../../src/conf", config_name="complete_taxonomy")
def rank(cfg: DictConfig):
    path = Path(cfg.taxonomy_folder)
    folders = [x for x in path.iterdir() if x.is_dir() and 'ensemble' not in str(x) and 'processed' not in str(x)]

    models_params = {'cso': ['LLM', 'Sim_Threshold'],
                     'LLM': ['LLM', 'prompt_type'],
                     'wikidata': ['Take_All', 'Types_Threshold', 'Max_Depth']}

    metrics = {'\# Roots': True, '\# New Terms': True, 'Missing': True}  # True -> Minimize, False -> Maximize
    for folder in folders:
        metric_file = folder / 'melted_metrics.csv'
        name = folder.stem.split('_')[0]
        if '-' in name:
            name = name.split('-')[0]
        res = []  # pd.DataFrame(columns=models_params[name] + ['Score'])
        if metric_file.exists():
            df = pd.read_csv(metric_file)
            df = df.fillna('NA')
            group = df.copy(deep=True).groupby('Metric')
            for metric, group_df in group:
                if metric in metrics:
                    sorted_df = group_df.sort_values(by='Value', ascending=metrics[metric])
                    scores = list(range(len(sorted_df)))
                    sorted_df['Score'] = scores
                    cols = models_params[name] + ['Score']
                    sorted_df = sorted_df[cols]
                    res.append(sorted_df)

        res = pd.concat(res)
        res = res.groupby(models_params[name]).sum()
        res = res.reset_index()
        res = res.sort_values(by='Score', ascending=True)  # Lower scores -> Better
        res.to_csv(folder / 'ranked_models.csv', index=False)
        res['Ranking'] = range(1, len(res) + 1)
        res = res[['Ranking'] + list(res.columns[:-1])]
        res.head(n=10).to_latex(folder / 'ranked_models.tex', index=False,
                                float_format="{:.2f}".format)


@hydra.main(version_base='1.3', config_path="../../src/conf", config_name="complete_taxonomy")
def rank_pp(cfg: DictConfig):
    path = Path(cfg.taxonomy_folder)
    folders = [x for x in path.iterdir() if x.is_dir() and 'ensemble' not in str(x) and 'processed' in str(x)]

    pp = ['cycle','bridge','abstract','minimization']
    exclude_pp = ['minimization']
    pp = [x for x in pp if x not in exclude_pp]
    models_params = {'cso': ['LLM', 'Sim_Threshold'] + pp,
                     'LLM': ['LLM', 'prompt_type'] + pp,
                     'wikidata': ['Take_All', 'Types_Threshold', 'Max_Depth'] + pp}

    metrics = {'\# Roots': True, '\# New Terms': True, 'Missing': True}  # True -> Minimize, False -> Maximize
    for folder in folders:
        metric_file = folder / 'melted_metrics.csv'
        name = folder.stem.split('_')[0]
        if '-' in name:
            name = name.split('-')[0]
        res = []  # pd.DataFrame(columns=models_params[name] + ['Score'])
        if metric_file.exists():
            df = pd.read_csv(metric_file)
            df = df.fillna('NA')
            df.drop(columns=exclude_pp, inplace=True)
            group = df.copy(deep=True).groupby('Metric')
            for metric, group_df in group:
                if metric in metrics:
                    sorted_df = group_df.sort_values(by='Value', ascending=metrics[metric])
                    scores = list(range(len(sorted_df)))
                    sorted_df['Score'] = scores
                    cols = models_params[name] + ['Score']
                    sorted_df = sorted_df[cols]
                    res.append(sorted_df)

        res = pd.concat(res)
        res = res.groupby(models_params[name]).sum()
        res = res.reset_index()
        res = res.sort_values(by='Score', ascending=True)  # Lower scores -> Better
        res.to_csv(folder / 'ranked_models.csv', index=False)
        res['Ranking'] = range(1, len(res) + 1)
        res = res[['Ranking'] + list(res.columns[:-1])]
        res.head(n=10).to_latex(folder / 'ranked_models.tex', index=False,
                                float_format="{:.2f}".format)

if __name__ == '__main__':
    rank()
    rank_pp()
