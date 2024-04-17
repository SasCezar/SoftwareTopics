import json
from collections import Counter

import pandas as pd
from wikidata.client import Client


def get_wikitypes_gitranking_ad():
    ids = ['Q102190569']
    client = Client()
    with open('../../data/raw/gitranking.jsonl') as inf:
        for line in inf:
            q_id = json.loads(line)['Wikidata ID']
            ids.append(q_id)

    types = Counter()
    for q_id in ids:
        data = client.get(q_id, load=True)
        t = [x['mainsnak']['datavalue']['value']['id'] for x in
             data.data['claims'].get('P31', [])]
        types.update(t)


    types = types.most_common()
    df = pd.DataFrame(types, columns=['type', 'count'])
    df.to_csv('../../data/interim/wikidata_types.csv', index=False)


if __name__ == '__main__':
    get_wikitypes_gitranking_ad()
