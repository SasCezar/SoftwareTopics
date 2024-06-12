import random

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


class LLMPatch(AbstractCompletion):
    def __init__(self, model, prompt_type):
        self.name = "LLM-Patch"
        self.model = model
        self.llm = ChatOpenAI(model_name=model,
                              openai_api_key='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')  # API key is looked up in the environment variables
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))
        self.prompt_type = prompt_type
        self.examples = []

        patch = PromptTemplate.from_template("""
            You are a helpful assistant tasked to pair terms to the hypernym to which they should belong. If it does not belong to any, answer None. 
            Given a term, provide the hypernym for the term.
            Multiple answers are allowed, and should be separated by a comma. Keep the answer concise, in CSV format, without any extra. 
            For example: 
            parent1
            parent1,parent2,parent3
            None
            Given the following taxonomy:
            {taxonomy}
            What is the hypernym of {term}?
        """)

        self.prompt_format = {
            "patch": (self.format_patch, patch)
        }

        self.params = {'llm': self.model, 'prompt_type': self.prompt_type}

    def complete(self, taxonomy: Taxonomy) -> Taxonomy:
        pairs = []
        str_pairs = "\n".join(['{}, {}'.format(hyponym, hypernym) for hyponym, hypernym, _ in taxonomy.pairs])
        lower_terms = {term.lower(): term for term in taxonomy.terms}
        for term in tqdm(taxonomy.missing):
            response = self.llm.invoke(self.format_prompt(pairs=str_pairs, term=term))
            logger.info('Response: {}'.format(response.content))
            res = [x.strip() for x in response.content.split(",")]
            if len(res) == 1 and res[0] == "None":
                continue

            for hypernym in res:
                if hypernym.lower() == 'none':
                    continue
                if hypernym.lower() in lower_terms:
                    hypernym = lower_terms[hypernym.lower()]
                print(f"Term: {term}, Hypernym: {hypernym}")
                if term != hypernym:
                    pairs.append([term, hypernym, self.name])

        taxonomy.pairs.extend(pairs)
        print(f"Pairs: {taxonomy.pairs}")
        taxonomy.update()
        taxonomy.other['params'] = self.params

        return taxonomy

    def format_prompt(self, pairs, term):
        function, template = self.prompt_format[self.prompt_type]
        prompt = function(pairs, term, template)
        logger.info('Prompt: {}'.format(prompt))
        return prompt

    @staticmethod
    def format_patch(pairs, term, template):
        return template.format_prompt(taxonomy=pairs, term=term)
