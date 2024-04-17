import random
from collections import deque

import numpy as np
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from tqdm import tqdm

from completion.completion import AbstractCompletion
from entity.taxonomy import Taxonomy

np.random.seed(1337)
random.seed(1337)


class LLMIterCompletion(AbstractCompletion):
    def __init__(self, model, prompt_type):
        self.name = "LLM_Iter"
        self.model = model
        self.llm = ChatOpenAI(model_name=model,
                              openai_api_key='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')  # API key is looked up in the environment variables
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
        self.prompt_type = prompt_type
        self.examples = []

        simple = PromptTemplate.from_template("""
                You are a helpful assistant tasked to pair terms to the hypernym to which they should belong. If it does not belong to any, answer None. 
                Given a term, provide the hypernym for the term.
                Multiple answers are allowed, and should be separated by a comma. Keep the answer concise, in CSV format, without any extra. 
                For example: 
                parent1
                parent1,parent2,parent3
                None
                What is the hypernym of {term}?
                """.strip())

        w_taxo = PromptTemplate.from_template("""
                You are a helpful assistant tasked to pair terms to the hypernym to which they should belong. If it does not belong to any, answer None. 
                Given a term, provide the hypernym for the term. The hypernym should be a term from the taxonomy.
                Multiple answers are allowed, and should be separated by a comma. Keep the answer concise, in CSV format, without any extra. 
                For example: 
                parent1
                parent1,parent2,parent3
                None
                This is the list of possible terms: 
                {taxonomy}
                What is the hypernym of {term}?
            """.strip())


        self.prompt_format = {
            "simple": (self.format_simple, simple),
            "w_taxo": (self.format_w_taxo, w_taxo)
        }

        self.params = {'llm': self.model, 'prompt_type': self.prompt_type}

    def complete(self, taxonomy: Taxonomy) -> Taxonomy:
        pairs = []
        lower_terms = {term.lower(): term for term in taxonomy.terms}
        seen = set()
        stack = deque(taxonomy.terms)
        p_bar = tqdm()
        str_terms = "\n".join(taxonomy.terms)
        while stack:
            p_bar.update(1)
            logger.info(f"Stack: {len(stack)}")
            term = stack.pop()
            response = self.llm.invoke(self.format_prompt(taxonomy=str_terms, term=term))
            print(f"Term: {term}, Response: {response.content}")
            res = [x.strip() for x in response.content.split(",")]
            if len(res) == 1 and res[0] == "None":
                continue
            taxonomy.missing.pop(taxonomy.missing.index(term)) if term in taxonomy.missing else None
            for hypernym in res:
                if hypernym.lower() in lower_terms:
                    hypernym = lower_terms[hypernym.lower()]
                if hypernym not in seen:
                    stack.append(hypernym)
                    seen.add(hypernym)
                pairs.append((term, hypernym, self.name))

        taxonomy.pairs.extend(set(pairs))
        taxonomy.pairs = list(set(taxonomy.pairs))
        taxonomy.update()
        taxonomy.other['params'] = self.params
        return taxonomy

    @staticmethod
    def load_examples(taxonomy):
        if not taxonomy.pairs:
            return ""
        examples = random.sample(taxonomy.pairs, 10)
        examples = "\n".join(["{} -> {}".format(hyponym, hypernym) for hypernym, hyponym in examples])
        return examples

    def format_prompt(self, taxonomy, term):
        function, template = self.prompt_format[self.prompt_type]
        return function(taxonomy, term, template)

    @staticmethod
    def format_simple(_, term, template):
        return template.format_prompt(term=term)

    @staticmethod
    def format_w_taxo(taxonomy, term, template):
        return template.format_prompt(taxonomy=taxonomy, term=term)
