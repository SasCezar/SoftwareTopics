from pathlib import Path

import hydra
import numpy as np
import pandas as pd
from omegaconf import DictConfig
from agreement import krippendorffs_alpha, cohens_kappa
from agreement.utils.transform import pivot_table_frequency


def load_data(file: Path):
    annotators_file = pd.read_excel(file, sheet_name='Annotators', index_col=None, header=None)
    annotators_file = {x[0]: x[1] for x in annotators_file.values}
    annotators_file_map = {}
    for key, value in annotators_file.items():
        aid = annotators_file_map.get(value, value)
        annotators_file_map[key] = aid[1]

    print(annotators_file_map)
    sheets_dict = pd.read_excel(file, sheet_name=None)

    all_sheets = []

    for name, sheet in sheets_dict.items():
        if name == 'Annotators':
            continue
        sheet['annotator'] = annotators_file_map[name]
        print(name, annotators_file_map[name])

        all_sheets.append(sheet)

    full_table = pd.concat(all_sheets)
    full_table.reset_index(inplace=True, drop=True)
    print('Size', full_table.shape)
    return full_table


def make_dataset(df):
    df['is_correct'] = df['is_correct'].apply(lambda x: 0 if x == -1 else x)
    df['group'] = df.groupby(['term', 'hypernym']).ngroup()
    df = df[df.group.duplicated(keep=False)]
    print("UNIQUE", df['group'].nunique())
    print("TOTAL", len(df))
    dataset = np.array([[x, y, z] for x, y, z in zip(df['group'], df['annotator'], df['is_correct'])])
    return dataset


@hydra.main(version_base='1.3', config_path='../../src/conf', config_name='process_taxonomy')
def evaluate_annotations(cfg: DictConfig):
    file = Path(cfg.result) / "software_taxonomy_validation_anonymized.xlsx"
    df = load_data(file)
    df['is_correct'] = df['is_correct'].fillna('0').astype(int)
    dataset = make_dataset(df)
    model = "gpt-4-1106-preview"

    questions_answers_table = pivot_table_frequency(dataset[:, 0], dataset[:, 2])
    users_answers_table = pivot_table_frequency(dataset[:, 1], dataset[:, 2])
    print('Krippendorff\'s alpha:', krippendorffs_alpha(questions_answers_table))

    kappa = cohens_kappa(questions_answers_table, users_answers_table)
    print('Cohen\'s kappa:', kappa)

    """Pairwise agreement matrix"""
    res = pairwise_agreement(df)
    res = pd.DataFrame(res)
    res.to_csv(Path(cfg.result) / 'pairwise_agreement.csv', index=False)

    gpt_file = Path(cfg.result) / f"llm_taxo_eval_{model}.csv"
    gpt_df = pd.read_csv(gpt_file)
    gpt_df['annotator'] = 99
    gpt_df['is_correct'] = gpt_df['is_correct'].apply(lambda x: '0' if x == '-1' or x == -1 else x)
    df = pd.concat([df, gpt_df])
    df['is_correct'] = df['is_correct'].fillna('0').astype(int)
    df['annotator'] = df['annotator'].astype(int)

    df = df.dropna(subset=['term', 'hypernym'])
    df.to_csv(Path(cfg.result) / 'software_taxonomy_validation_anonymized_merged_w_LLM.csv', index=False)
    dataset = make_dataset(df)

    questions_answers_table = pivot_table_frequency(dataset[:, 0], dataset[:, 2])
    users_answers_table = pivot_table_frequency(dataset[:, 1], dataset[:, 2])
    print('Krippendorff\'s alpha w LLM:', krippendorffs_alpha(questions_answers_table))

    kappa = cohens_kappa(questions_answers_table, users_answers_table)
    print('Cohen\'s kappa w LLM:', kappa)

    """Pairwise agreement matrix"""
    res = pairwise_agreement(df)
    res = pd.DataFrame(res)
    res.to_csv(Path(cfg.result) / 'pairwise_agreement_w_LLM.csv', index=False)


def pairwise_agreement(df):
    print(df)
    annotators = set(df['annotator'].tolist())
    res = []
    for i in annotators:
        for j in annotators:
            if i < j:
                subdf = df.copy(deep=True)
                print('Before', df.shape)
                subdf = subdf[subdf['annotator'].isin([i, j])]
                #
                print('After', subdf.shape)
                # annotator_i = sub_df[sub_df['annotator'] == i]
                # annotator_j = sub_df[sub_df['annotator'] == j]
                subdf = make_dataset(subdf)

                if len(subdf) > 0:
                    try:
                        ag = krippendorffs_alpha(pivot_table_frequency(subdf[:, 0], subdf[:, 2]))
                        k = cohens_kappa(pivot_table_frequency(subdf[:, 0], subdf[:, 2]),
                                         pivot_table_frequency(subdf[:, 1], subdf[:, 2]))
                    except:
                        ag = 0
                    if np.isnan(ag):
                        ag = 0
                    res.append({'annotator1': i, 'annotator2': j, 'agreement': ag, 'K': k, 'n': np.ceil(len(subdf)/2)})
    return res


if __name__ == '__main__':
    evaluate_annotations()
