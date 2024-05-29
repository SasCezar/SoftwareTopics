from typing import Dict

from loguru import logger
from pandas import DataFrame
from paretoset import paretoset

from optimizer.optimizer import AbstractOptimizer


class ParetoOptimizer(AbstractOptimizer):
    def __init__(self):
        super().__init__()
        self.name = 'Pareto'

    def optimize(self, samples: DataFrame, metrics: Dict, attributes):
        df = samples[samples['Metric'].isin(metrics.keys())]

        df = df.pivot_table(
            values='Value',
            index=attributes,
            columns='Metric'
        )
        df = df.reset_index()

        df_pareto = df.drop(columns=attributes)
        if len(df_pareto) == 0:
            df['Pareto'] = [False] * len(df)
            return df

        senses = [metrics[col]['optimization'] for col in df_pareto.columns]
        mask = paretoset(df_pareto, sense=senses)
        df['Pareto'] = mask
        df = df[df['Pareto']]
        logger.info(f'Percent of Paretoset row {sum(mask) / len(mask) * 100}')
        return df
