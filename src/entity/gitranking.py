import json


class GitRanking:
    def __init__(self, path):
        self.terms = {}
        self.aliases = {}
        self.load(path)

    def load(self, path):
        terms = {}
        aliases = {}
        with open(path) as f:
            for line in f:
                term = json.loads(line)
                terms[term['Wikidata Title']] = term['Wikidata ID']
                aliases[term['Wikidata Title']] = term['Wikidata Aliases'] + term["GitHub Topic"]

        self.terms = terms
        self.aliases = aliases
