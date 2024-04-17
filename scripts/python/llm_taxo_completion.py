import random
from pathlib import Path

import numpy as np
import pandas as pd
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from more_itertools import flatten
from tqdm import tqdm


def load_taxonomy(path):
    df = pd.read_csv(path)
    return [(hypernym, hyponym) for hypernym, hyponym in zip(df['hyponym'], df['hypernym'])]


def load_data(taxonomy_path, unmatched_path):
    pairs = load_taxonomy(taxonomy_path)
    taxonomy = list(set(flatten(pairs)))
    taxonomy = "\n".join(taxonomy)
    examples = random.sample(pairs, 10)
    examples = "\n".join(["{} -> {}".format(hyponym, hypernym) for hypernym, hyponym in examples])
    unmatched = pd.read_csv(unmatched_path)['unmatched'].tolist()

    unmatched = [x.replace("https://cso.kmi.open.ac.uk/topics/", "") for x in unmatched]

    return taxonomy, examples, unmatched


def main():
    # set seed for random
    np.random.seed(1337)
    random.seed(1337)
    taxonomy_path = Path('../../data/interim/gitranking_cso.csv')
    unmatched_path = Path('../../data/interim/gitranking_cso_unmatched.csv')
    taxonomy, examples, unmatched = load_data(taxonomy_path, unmatched_path)
    print(examples)
    print(unmatched)

    model ="gpt-4-1106-preview"

    llm = ChatOpenAI(openai_api_key="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",
                     model=model)

    single_template = PromptTemplate.from_template("""
    You are a helpful assistant tasked to pair terms to their hypernym it should belong. If it does not belong to any, answer ["None"]. 
    Keep the answer on point and only use the terms provided. Multiple answers are allowed, and should be separated by a a comma.
    Here are some examples: 
    {examples}
    This is list of possible terms: 
    {taxonomy}
    What is the hypernym of {term}?
    """)

    set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    res = []
    for term in tqdm(unmatched):
        hypernym = llm.invoke(single_template.format(examples=examples, taxonomy=taxonomy, term=term))
        print(hypernym.content)
        res.append((term, hypernym.content))

    df = pd.DataFrame(res, columns=['term', 'hypernym'])
    df.to_csv(f"../../data/interim/gitranking_cso_completed_{model}.csv", index=False)

if __name__ == '__main__':
    main()
