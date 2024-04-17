import networkx as nx
import pandas as pd
from loguru import logger
from sklearn.cluster import KMeans

from entity.taxonomy import Taxonomy
from processing.processing import AbstractProcessing


class AbstractTermsRemovalProcessing(AbstractProcessing):
    def __init__(self, ranked_terms_path, level):
        self.graph = nx.DiGraph()
        self.clusters = self.load_clusters(ranked_terms_path)
        self.level = level

    def process(self, taxonomy: Taxonomy) -> Taxonomy:
        self.graph.add_edges_from([(term, parent) for term, parent, _ in taxonomy.pairs])
        taxonomy.post_process['clusters'] = self.clusters
        top = {term for term, _ in self.clusters.items() if _ <= self.level}
        remove_ancestors = []
        skipped = []
        for term in top:
            if term not in self.graph:
                skipped.append(term)
                continue
            ancestors = nx.ancestors(self.graph.reverse(copy=True), term)
            for ancestor in ancestors:
                decent = nx.descendants(self.graph, ancestor)
                in_git = any([x in taxonomy.gitranking_qid for x in decent])
                if ancestor in taxonomy.gitranking_qid or in_git:
                    continue
                remove_ancestors.append(ancestor)
        taxonomy.post_process['removed_ancestors'] = remove_ancestors
        taxonomy.post_process['skipped'] = skipped
        logger.info(f"Removed {len(remove_ancestors)} ancestors and skipped {len(skipped)} terms")
        taxonomy.pairs = [(term, parent, name) for term, parent, name in taxonomy.pairs if term not in remove_ancestors]
        return taxonomy

    def load_clusters(self, ranked_terms_path):
        df = pd.read_csv(ranked_terms_path, sep=',')
        clusters = KMeans(n_clusters=8, random_state=0, n_init='auto').fit_predict(df[['mean']])
        clusters = self.sort_clusters(clusters, df)
        clusters = {term: cluster for term, cluster in zip(df['topic'], clusters)}
        return clusters

    def sort_clusters(self, clusters, df):
        """Sort clusters by the mean value of the cluster"""
        """The cluster with the lowest mean value will be assigned to 0, the second lowest to 1, and so on.
        """
        df['cluster'] = clusters
        df = df.groupby('cluster')['mean'].mean().sort_values(key=lambda x: -x).reset_index()
        mapping = {cluster: i for i, cluster in enumerate(df['cluster'])}
        return [mapping[cluster] for cluster in clusters]
