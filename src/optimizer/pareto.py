from abc import ABC
from typing import Dict

from pandas import DataFrame
from paretoset import paretoset

from optimizer.optimizer import AbstractOptimizer


class ParetoOptimizer(AbstractOptimizer):
    def __init__(self):
        super().__init__()
        self.name = 'Pareto'

    def optimize(self, samples: DataFrame, metrics: Dict, attributes):
        df = samples[samples['Metric'].isin(metrics.keys())]
        df = df.pivot(
            values='Value',
            index=attributes,
            columns='Metric'
        )

        df = df.drop(attributes)

        senses = [metrics[col] for col in df.columns]
        mask = paretoset(df, sense=senses)
        df['Pareto'] = mask

        return df
