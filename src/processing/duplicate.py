import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from entity.taxonomy import Taxonomy
from processing.processing import AbstractProcessing


class DuplicateRemovalProcessing(AbstractProcessing):
    def __init__(self, sentence_transformer='all-mpnet-base-v2'):
        self.embedding = SentenceTransformer(sentence_transformer)
        self.threshold = 0.9

    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        """
        Remove duplicates from the taxonomy
        :param taxonomy:
        :return:
        """
        embeddings = self.embedding(taxonomy.terms)
        similarities = cosine_similarity(embeddings, embeddings)
        similarities = np.fill_diagonal(similarities, 0)
        similarities = np.tril(similarities, k=-1)
        duplicates = np.where(similarities > self.threshold)
        ## Get the indices of the duplicates
        duplicates = [(taxonomy.terms[i], taxonomy.terms[j]) for i, j in zip(*duplicates)]
        # Join the duplicates
        taxonomy = taxonomy.update()
        return taxonomy
