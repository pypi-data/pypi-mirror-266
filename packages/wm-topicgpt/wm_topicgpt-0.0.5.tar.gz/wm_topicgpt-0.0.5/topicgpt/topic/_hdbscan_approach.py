import numpy as np
from umap import UMAP
from sklearn.cluster import HDBSCAN
from sklearn.metrics.pairwise import pairwise_distances
from ..base import GeneratorMixin
from ._cluster_base import Cluster
from ..feature_extraction import TopicGenerator
    

class HDBSCANTopicGenerator(GeneratorMixin):

    def __init__(self, reduced_dim, n_neighbors, min_cluster_percent, topk=5, 
                 model_name="gpt-35-turbo", temperature=0.5, verbose=True):
        self.reduced_dim = reduced_dim
        self.n_neighbors = n_neighbors
        self.min_cluster_size = min_cluster_percent
        self.topk = topk
        self.verbose = verbose
        self.nodes = 1
        self.topic_generator = TopicGenerator(model_name, temperature)

    def _dfs_build_clusters(self, root, n_neighbors, tier):
        if self.verbose:
            print("\t" * tier, "tier:", tier, "#data:", len(root.texts), "n_neighbors:", n_neighbors)

        reducer = UMAP(n_neighbors=5, n_components=self.reduced_dim, metric='cosine')
        reduced_embeddings = reducer.fit_transform(root.embeddings)

        cluster = HDBSCAN(min_cluster_size=self.min_cluster_size, n_jobs=-1)
        cluster.fit(reduced_embeddings)
        
        for label in sorted(set(cluster.labels_)):
            indices = [i for i, clabel in enumerate(cluster.labels_) if clabel == label]
            cluster_texts = [root.texts[i] for i in indices]
            cluster_embeddings = [root.embeddings[i] for i in indices]
            if self.verbose:
                print("\t" * tier, "cluster label:", label, "#data:", len(cluster_texts))

            if len(cluster_texts) <= self.min_cluster_size:
                root.children.append(Cluster(texts=cluster_texts, embeddings=cluster_embeddings))
            else:
                next_neighbors = int(n_neighbors // 2)
                if next_neighbors < 2:
                    root.children.append(Cluster(texts=cluster_texts, embeddings=cluster_embeddings))
                else:
                    sub_root = self._dfs_build_clusters(Cluster(texts=cluster_texts, embeddings=cluster_embeddings), next_neighbors, tier+1)
                    root.children.append(sub_root.children[0] if len(sub_root.children) == 1 else sub_root)
        return root.children[0] if len(root.children) == 1 else root

    def build_cluster_tree(self, texts, embeddings):
        self.nodes = 1
        self.min_cluster_size = int(self.min_cluster_size * len(texts))
        root = Cluster(texts=texts, embeddings=embeddings)
        root = self._dfs_build_clusters(root, self.n_neighbors, tier=0)
        return root
        
    def _tree_traversal(self, root):
        if root.size is None:
            root.size = len(root.texts)
        if root.percent is None:
            root.percent = 1.

        if root.centroid is None:
            root.centroid = np.mean(np.array(root.embeddings), axis=0)
        dists = pairwise_distances(np.array([root.centroid]), np.array(root.embeddings))[0]
        root.within_cluster_dist = np.mean(dists)
        root.closest = np.argsort(dists)[:self.topk]
        response = self.topic_generator.transform(root)
        root.topic = response['topic']
        root.description = response['description']

        for child in root.children:
            child.size = len(child.texts)
            child.percent = round(child.size / root.size, 3)
            self._tree_traversal(child)

    def fill_cluster_tree(self, root):
        self._tree_traversal(root)

    def plot_cluster_tree(self, root, last=True, header=''):
        elbow = "└────"
        pipe = "│  "
        tee = "├────"
        blank = "   "
        print(f"{header}{elbow if last else tee} {root.topic} - {root.description} ({root.size} | {root.percent*100:.1f}%)")
        
        child_size = len(root.children)
        self.nodes += child_size
        if child_size > 0:
            for i, c in enumerate(root.children):
                self.plot_cluster_tree(c, header=header + (blank if last else pipe), last=i == child_size - 1)

    def predict(self, texts, embeddings):
        root = self.build_cluster_tree(texts, embeddings)
        self.fill_cluster_tree(root)
        if self.verbose:
            self.plot_cluster_tree(root)
        return root