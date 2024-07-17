import random
from pathlib import Path

import hydra
import numpy as np
import pandas as pd
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from more_itertools import flatten
from omegaconf import DictConfig
from tqdm import tqdm

from entity import Taxonomy


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


@hydra.main(version_base='1.3', config_path='../../src/conf', config_name='process_taxonomy')
def main(cfg: DictConfig):
    # set seed for random
    np.random.seed(1337)
    random.seed(1337)
    taxonomy_path = Path(
        '/home/sasce/PycharmProjects/SoftwareTopics/data/result/taxonomy/cascade/topsis/patched_gitranking_ensemble_patched.json')
    taxonomy = Taxonomy.load(taxonomy_path)
    model = "gpt-3.5-turbo"

    llm = ChatOpenAI(model=model)

    template = PromptTemplate.from_template("""
    You are an expert in domain relationships and knowledge categorization. Your task is to analyze pairs of terms and determine their relationship based on the following criteria:
    - 1 (Subdomain Relationship): One term is a specific subdomain or subset of the other.
    - 0 (No Relationship): The terms have no significant relationship.
    - -1 (Related but Not Subdomain): The terms are related but neither is a subdomain of the other.
    For each pair of terms provided, identify and categorize their relationship. Only provide the classification (1, 0, or -1) without any explanation.
    Are the terms in the pair related as subdomain, unrelated, or related but not subdomain?
    {pair}
    """)

    #set_llm_cache(SQLiteCache(database_path=".my.db"))

    res = []
    for pair in tqdm(taxonomy.pairs):
        txt_pair = ",".join(pair[:2])
        print(txt_pair)
        prompt = template.format(pair=txt_pair)
        print(prompt)
        out = llm.invoke(prompt)
        print(out.content)
        res.append((pair[0], pair[1], model, out.content, ''))

    df = pd.DataFrame(res, columns=['term', 'hypernym', 'annotator', 'is_correct', 'wrong_term(s)'])
    df.to_csv(Path(cfg.result) / f"llm_taxo_eval_{model}.csv", index=False)


if __name__ == '__main__':
    main()
