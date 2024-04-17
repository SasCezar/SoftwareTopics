from pathlib import Path

import pandas as pd
from tqdm import tqdm
import pingouin as pg


def compute_correlations():
    path = Path('../../data/interim/taxonomy')
    folders = list(path.iterdir())

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
            # corr = corr.stack().reset_index()
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
            metrics = ["\# Nodes", "\# Edges", "\# Leafs", "\# Roots", "\# Bridges", "\# Intermediate", "\# Self Loops",
                       "\# Cycles", "\#  CC", "Pairs Acc"]
            rows = []
            # measure the correlation between the metrics and the post-processing columns
            for metric in metrics:
                for process in processing:
                    print(f'{metric} and {process}')
                    df_copy = df.copy(deep=True)
                    others = [x for x in processing if x != process]
                    df_copy['total'] = df_copy[others].sum(axis=1)
                    df_copy = df_copy[df_copy['total'] == 0]
                    corr = pg.corr(x=df_copy[process], y=df_copy[metric], method='pearson')['r'][0]
                    rows.append([metric, process, corr])
            print(corr)
            """Convert the correlation matrix to a dataframe X, Y, correlation"""
            # corr = corr.reset_index().melt(id_vars='index')
            # corr.columns = ['X', 'Y', 'correlation']
            corr = pd.DataFrame(rows, columns=['X', 'Y', 'correlation'])
            """Save the correlation matrix"""
            corr.to_csv(file.parent / f'{file.stem}_correlation_postprocessing.csv', index=False)


if __name__ == '__main__':
    compute_correlations()
