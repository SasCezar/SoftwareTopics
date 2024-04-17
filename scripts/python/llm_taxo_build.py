import copy
import random
from pathlib import Path

import numpy as np
import pandas as pd
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from tqdm import tqdm


def load_taxonomy(path):
    """Loads data from a JSONL file. The term is in the Wikidata Title field"""
    df = pd.read_json(path, lines=True)
    return df['Wikidata Title'].tolist()


def main():
    # set seed for random
    np.random.seed(1337)
    random.seed(1337)
    taxonomy_path = Path('../../data/raw/gitranking.jsonl')
    taxonomy = load_taxonomy(taxonomy_path)
    model = "gpt-4-1106-preview"
    #model = "gpt-3.5-turbo"
    llm = ChatOpenAI(openai_api_key="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",
                     model=model)

    single_template = PromptTemplate.from_template("""
    You are a helpful assistant tasked to pair terms to their hypernym it should belong. If it does not belong to any, answer ["None"]. 
    Keep the answer on point and only use the terms provided.
    This is list of possible terms: 
    {taxonomy}
    What is the hypernym of {term}?
    """)

    set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    res = []
    for term in tqdm(taxonomy):
        taxo_clean = copy.copy(taxonomy).pop(taxonomy.index(term))
        hypernym = llm.invoke(single_template.format(taxonomy=taxo_clean, term=term))
        print(hypernym.content)
        res.append((term, hypernym.content))

    df = pd.DataFrame(res, columns=['term', 'hypernym'])
    df.to_csv(f"../../data/interim/gitranking_completed_{model}.csv", index=False)


if __name__ == '__main__':
    main()
