from typing import Dict

from pandas import DataFrame

from optimizer.optimizer import AbstractOptimizer


class MCDMOptimizer(AbstractOptimizer):
    def __init__(self, name, algorithm):
        super().__init__()
        self.name = f'MCDM_{name}'
        self.algorithm = algorithm

    def optimize(self, samples: DataFrame, metrics: Dict, attributes):
        df = samples[samples['Metric'].isin(metrics.keys())]

        df = df.pivot_table(
            values='Value',
            index=attributes,
            columns='Metric'
        )
        df = df.reset_index()
        df_solve = df.drop(columns=attributes)

        self.algorithm()

