from typing import Dict

import numpy as np
from pandas import DataFrame

from optimizer.optimizer import AbstractOptimizer


class MCDMOptimizer(AbstractOptimizer):
    def __init__(self, name, algorithm):
        super().__init__()
        self.name = f'MCDM_{name}'
        self.algorithm = algorithm
        self.optimize_map = {'min': -1, 'max': 1}

    def optimize(self, samples: DataFrame, metrics: Dict, attributes):
        df = samples[samples['Metric'].isin(metrics.keys())]

        df = df.pivot_table(
            values='Value',
            index=attributes,
            columns='Metric'
        )
        df = df.reset_index()

        df_solve = df.drop(columns=attributes)

        if len(df_solve) == 0:
            df['Score'] = [0] * len(df)
            return df

        matrix = df_solve.to_numpy()
        weights = np.array([metrics[metric]['weight'] for metric in df_solve.columns])
        weights = weights/sum(weights)
        types = np.array([self.optimize_map[metrics[metric]['optimization']] for metric in df_solve.columns])
        try:
            res = [round(preference, 3) for preference in self.algorithm(matrix, weights, types)]
        except Exception as e:
            print(e)
            res = [0] * len(df)

        df['Score'] = res
        df = df.sort_values('Score', ascending=False)
        return df
