from typing import Dict

import pandas as pd
from pandas import DataFrame

from optimizer.optimizer import AbstractOptimizer


class ScoringOptimizer(AbstractOptimizer):
    def __init__(self):
        super().__init__()
        self.name = 'Scoring'
        self.optimize_map = {'min': True, 'max': False}

    def optimize(self, samples: DataFrame, metrics: Dict, attributes):
        group = samples.copy(deep=True).groupby('Metric')
        res = []
        for metric, group_df in group:
            if metric in metrics:
                sorted_df = group_df.sort_values(by='Value',
                                                 ascending=self.optimize_map[metrics[metric]['optimization']])
                scores = list(range(len(sorted_df))) * metrics[metric]['weight']
                sorted_df['Score'] = scores
                cols = attributes + ['Score']
                sorted_df = sorted_df[cols]
                res.append(sorted_df)
        res = pd.concat(res)
        res = res.groupby(attributes).sum()
        res = res.reset_index()
        res = res.sort_values(by='Score', ascending=True)

        return res
