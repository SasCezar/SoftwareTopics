from pathlib import Path

import hydra
import pandas as pd
import pingouin as pg
from omegaconf import DictConfig
from tqdm import tqdm


@hydra.main(version_base='1.3', config_path="../../src/conf", config_name="complete_taxonomy")
def compute_correlations(cfg: DictConfig):
    path = Path(cfg.taxonomy_folder)
    folders = [folder for folder in path.iterdir() if folder.is_dir()]

    for folder in folders:
        files = [x for x in folder.iterdir() if
                 'metrics.csv' in str(x) and 'melted' not in x.stem and 'processed' in folder.stem]
        for file in tqdm(files, desc=folder.stem):
            df = pd.read_csv(file)
            """Remove all rows where the following columns are not 0: cycle,bridge,abstract,minimization"""
            df = df[(df['cycle'] == 0) & (df['bridge'] == 0) & (df['abstract'] == 0) & (df['minimization'] == 0)]
            """Remove the columns"""
            df = df.drop(columns=['cycle', 'bridge', 'abstract', 'minimization'])
            """Correlation matrix"""
            corr = df.apply(lambda x: pd.factorize(x)[0]).corr()
            """Convert the correlation matrix to a dataframe X, Y, correlation"""
            corr = corr.reset_index().melt(id_vars='index')
            corr.columns = ['X', 'Y', 'correlation']
            """Save the correlation matrix"""
            corr.to_csv(file.parent / f'{file.stem}_correlation.csv', index=False)
            print(corr)
            df = pd.read_csv(file)
            """Measure the correlation for the excluded columns when each of the columns is 1 and the other are 0"""
            """Exclude all the cases where more than one column is 1"""
            df = df[(df['cycle'] + df['bridge'] + df['abstract'] + df['minimization']) <= 1]

            processing = ['cycle', 'bridge', 'abstract', 'minimization']
            metrics = {'nodes': '\# Nodes', 'edges': '\# Edges', 'roots': '\# Roots', 'leafs': '\# Leafs',
                       'parents': '\# Parents', 'max_parents': 'Max Parents', 'children': '\# Children',
                       'max_children': 'Max Children', 'bridges': '\# Bridges', 'inters': '\# Intermediate',
                       'num_self_loops': '\# Self Loops', 'num_cycles': '\# Cycles', 'CC': '\#  CC',
                       'DAG': 'Is DAG', 'new_terms': '\# New Terms'}.values()
            rows = []
            # measure the correlation between the metrics and the post-processing columns
            for metric in metrics:
                for process in processing:
                    print(f'{metric} and {process}')
                    df_copy = df.copy(deep=True)
                    others = [x for x in processing if x != process]
                    df_copy['total'] = df_copy[others].sum(axis=1)
                    df_copy = df_copy[df_copy['total'] == 0]
                    corr = pg.corr(x=df_copy[process], y=df_copy[metric], method='pearson')['r']['pearson']
                    rows.append([metric, process, corr])
            print(corr)
            """Convert the correlation matrix to a dataframe X, Y, correlation"""
            corr = pd.DataFrame(rows, columns=['Metric', 'pp_name', 'correlation'])
            corr.fillna(0, inplace=True)
            """Save the correlation matrix"""
            corr.to_csv(file.parent / f'{file.stem}_correlation_postprocessing.csv', index=False)


if __name__ == '__main__':
    compute_correlations()
