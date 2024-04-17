import json
from pathlib import Path

import pandas as pd
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from more_itertools import chunked, flatten
from tqdm import tqdm


def load_pairs():
    path = Path('../../data/interim/taxonomy')
    folders = list(path.iterdir())
    all_pairs = set()

    for folder in folders:
        files = [x for x in folder.iterdir() if x.suffix == '.json']
        for file in files:
            print(file)
            with open(file, 'r') as f:
                taxonomy = json.load(f)
                pairs = {(x[0], x[1]) for x in taxonomy['pairs']}
                all_pairs.update(pairs)

    return all_pairs


def evaluate(pairs):
    model = "gpt-4-1106-preview"
    llm = ChatOpenAI(openai_api_key="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",
                     model=model)

    single_template = PromptTemplate.from_template("""
    You are a helpful assistant tasked to evaluate pairs of terms based on whether they are in a hypernym-hyponym relation. 
    Given a pair of terms `term,parent` answer with 1 if the pair is a hypernym-hyponym relation, 0 otherwise.
    Keep the answer concise, in CSV format, without any extra. For example term,parent,0 or term,parent,1
    Are the following pairs hypernym-hyponym relations?
    {pairs}
    """.strip())

    set_llm_cache(SQLiteCache(database_path=".langchain.db"))
    chunks = list(chunked(pairs, 5))
    res = []
    for ch in tqdm(chunks):
        p = "\n".join([",".join(x[:2]) for x in ch])

        preds = llm.invoke(single_template.format_prompt(pairs=p))
        preds = [x.split(',')[-1] for x in preds.content.split("\n")]
        rs = [(x[0], x[1], r) for x, r in zip(ch, preds)]
        res.extend(rs)

    return res


def load_examples():
    path = Path('/home/sasce/Downloads/SoftwareTopics/data/raw/all_topics_freq.csv')
    df = pd.read_csv(path)
    positive = df[df['AD'] == 1].sample(50)['term'].tolist()
    positive = [(x.replace('-', ' '), '1') for x in positive]
    negative = df[df['AD'] == 0].sample(50)['term'].tolist()
    negative = [(x.replace('-', ' '), '0') for x in negative]
    return positive + negative


def is_ad(pairs):
    model = "gpt-3.5-turbo"
    examples = load_examples()
    examples = "\n".join([",".join(x) for x in examples])

    llm = ChatOpenAI(openai_api_key="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",
                     model=model)

    single_template = PromptTemplate.from_template("""
    You are a helpful assistant tasked with aiding a user in filtering a list of terms on whether they are software application domains or not. 
    Answer 1 if it is, 0 if it is not, and "Unsure" if you are unsure. Here are some examples:
    {examples}
    Are the following terms software application domains? Give the answer in the format: term,1 or term,0 or term,Unsure.
    {terms}
    """)

    set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    terms = flatten(pairs)
    chunks = list(chunked(terms, 5))
    res = []
    for ch in tqdm(chunks):
        p = "\n".join(ch)

        preds = llm.invoke(single_template.format_prompt(examples=examples, terms=p))
        print(preds.content)
        preds = [x.split(',')[-1] for x in preds.content.split("\n")]
        rs = [(x, r) for x, r in zip(ch, preds)]
        res.extend(rs)

    return res


if __name__ == '__main__':
    df = pd.read_csv('pairs_llm_results.csv')
    already = set([(x[0], x[1]) for x in df.values])
    pairs = load_pairs()
    print(len(pairs))
    pairs = pairs - already
    print(len(pairs))
    result = evaluate(pairs)
    df_new = pd.DataFrame(result, columns=['term', 'parent', 'pred'])
    df = pd.concat([df, df_new])
    df.to_csv('results_all.csv', index=False)
    # rt = is_ad(pairs)
    # df = pd.DataFrame(rt, columns=['term', 'pred'])
    # df.to_csv('ad_results_100_examples.csv', index=False)
