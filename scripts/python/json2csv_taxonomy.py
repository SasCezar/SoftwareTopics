import string
from collections import deque

import pandas as pd

from entity import Taxonomy


def convert(file_path):
    taxo = Taxonomy.load(file_path)
    df = pd.DataFrame(taxo.pairs, columns=['term', 'hypernym', 'src'])
    df.to_csv(file_path.replace('json', 'csv'), index=False)
    return df


def assign_annotator(annotators, elements):
    res = []
    num = elements // annotators
    last = None
    for a in string.ascii_uppercase[:annotators]:
        res.extend([a] * num)
        last = a

    if len(res) < elements:
        res.extend([last] * abs(len(res) - elements))

    return res


def assign_annotators(annotators, df, k=3):
    pred_w_annot = []
    annot_pack = assign_annotator(annotators, len(df))
    for i in range(k):
        df_w_pred = df.copy(deep=True)
        annot_pack = deque(annot_pack)
        annot_pack.rotate(len(df) // annotators)
        df_w_pred['annotator'] = list(annot_pack)
        pred_w_annot.append(df_w_pred)

    pred_w_annot = pd.concat(pred_w_annot)
    return pred_w_annot


def to_xlsx(df, filename):
    with pd.ExcelWriter(filename) as writer:
        for group, data in df.groupby('annotator'):
            data.to_excel(writer, sheet_name=group, index=False)


if __name__ == '__main__':
    file_path = '/home/sasce/PycharmProjects/SoftwareTopics/data/result/taxonomy/cascade/topsis/patched_gitranking_ensemble_patched.json'
    df = convert(file_path)
    num_annotators = 8
    df = assign_annotators(num_annotators, df)
    df['is_correct'] = None
    df['wrong_term(s)'] = None
    to_xlsx(df, file_path.replace('.json', '_annotation.xlsx'))
