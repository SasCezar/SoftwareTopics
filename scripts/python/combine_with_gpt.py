from pprint import pprint

import pandas as pd
from more_itertools import flatten


def load_taxonomy(path):
    df = pd.read_csv(path)
    terms = flatten([(hypernym, hyponym) for hypernym, hyponym in zip(df['hyponym'], df['hypernym'])])
    return df, list(terms)


def clean(b):
    if "natural_sciences" in b:
        b = "science"

    if " -> " in b:
        b = b.split(" -> ")[1]
    if " is " in b:
        b = b.split(" is ")[1]

    if "," in b:
        b = [x.replace(".", "").strip().replace('natural_sciences', 'science') for x in b.split(",")]
        return b

    b = b.replace(".", "").strip()
    return [b]


def combine(taxonomy_path, completed_path, model):
    taxonomy, terms = load_taxonomy(taxonomy_path)
    missing = pd.read_csv(f'../../data/interim/gitranking_cso_unmatched.csv')
    missing = [x.replace("https://cso.kmi.open.ac.uk/topics/", '') for x in missing['unmatched'].tolist()]
    terms = terms + missing
    completed = load_completed(completed_path)
    missing = []
    none = []
    for (a, b) in completed:
        if type(b) != str:
            none.append((a, b))
            completed.remove((a, b)) if (a, b) in completed else None
            completed.append((a, "None"))
            continue
        bs = clean(b)
        for bc in bs:
            if bc not in terms:
                print('bc', bc, b)
                missing.append((a, b))
                completed.remove((a, b)) if (a, b) in completed else None
            else:
                completed.remove((a, b)) if (a, b) in completed else None
                completed.append((a, bc))

    completed = [(a.replace('natural_sciences', 'science'), b.replace('natural_sciences', "science")) for (a, b) in
                 completed]
    completed = pd.DataFrame(completed, columns=['hypernym', 'hyponym'])
    assert "natural_sciences" not in list(flatten(completed.values.tolist()))
    taxonomy = pd.concat([taxonomy, completed], ignore_index=True, axis=0)
    taxonomy.to_csv(f'../../data/result/gitranking_cso_{model}.csv', index=False)
    print(f'missing {len(missing)}')
    pprint(missing)
    # print(f'none {len(none)}')
    # pprint(none)
    return missing


def load_completed(completed_path):
    completed = pd.read_csv(completed_path)
    completed = completed[['term', 'hypernym']]
    completed = completed.values.tolist()
    completed = [tuple(x) for x in completed]
    return completed


if __name__ == '__main__':
    model = "gpt-4-1106-preview"
    completed_path = f'../../data/interim/gitranking_cso_completed_{model}.csv'
    taxonomy_path = '../../data/interim/gitranking_cso.csv'
    missing_a = combine(taxonomy_path, completed_path, model)
    model = "gpt-3.5-turbo"
    missing_b = combine(taxonomy_path, completed_path, model)
    intersection = set(missing_a).intersection(set(missing_b))
    print(f'intersection {len(intersection)}')
    pprint(intersection)
