from pathlib import Path

import hydra
import pandas as pd
from omegaconf import DictConfig


@hydra.main(version_base='1.3', config_path='../../src/conf', config_name='process_taxonomy')
def extract_examples(cfg: DictConfig):
    df = pd.read_csv(Path(cfg.result) / 'software_taxonomy_validation_anonymized_merged_w_LLM.csv')
    """Group by term and hypernym and sum by the 'is_correct' column"""
    res = df.groupby(['term', 'hypernym']).agg({'is_correct': ['sum']}).reset_index()
    """Rename the columns"""
    res.columns = ['term', 'hypernym', 'counts']
    """Assign '>3' for values that are grater than 3 in counts"""
    res['counts'] = res['counts'].apply(lambda x: '$>$3' if x > 3 else x)
    m = 5
    """Create a latex table where for each group (0,1,2,3,>3) we have just 5 examples. The table has 3 columns, term, hypernym, and the counts only. The sampling is on the count"""
    res = res.groupby(['counts']).apply(lambda x: x.sample(m)).reset_index(drop=True)
    """Make first letter uppercase"""
    res['term'] = res['term'].str.capitalize()
    res['hypernym'] = res['hypernym'].str.capitalize()
    """Save the table to a latex file"""
    res.to_latex(Path(cfg.result) / 'examples.tex', index=False)

if __name__ == '__main__':
    extract_examples()