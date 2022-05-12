from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.metrics import silhouette_score

from sklearn import preprocessing

from scipy.cluster.vq import vq

import fastcluster
import scipy.cluster
import numpy as np

from write.writer import write_linkage_matrix

class Clusterer:

    def __init__(self, pd_events_fv, config):
        # properties
        self.pd_events_fv = pd_events_fv
        self.config = config
        self._pred_labels = None

    def cluster(self, vectors, n_clusters=50):
        """
        Clusters the given feature vectors

        :vectors: the vector representation to cluster
        :clusterer: the cluster algorithm (k_means, agglomerative)
        :n_clusters: the number of clusters to generate
        :metric: the metric for the clusterer
        """
        if self.config.clust == 'k_means':
            self._pred_labels = self.k_means(vectors, n_clusters)
        elif self.config.clust == 'agglomerative':
            self._pred_labels = self.agglomerative(vectors, n_clusters, metric=self.config.sim_metric)


    def evaluate(self):
        """
        Computes the distribution of the computed clusters.
        """
        # distribution of clusters
        unique, counts = np.unique(self._pred_labels, return_counts=True)
        distribution = dict(zip(unique, counts))

        return distribution

    # K-Means
    def k_means(self, vectors, n_clusters):
        vector_norm = vectors
        sils = dict()
        temp_labels = dict()
        curr_clust = n_clusters
        #for curr_clust in range(2, n_clusters+1, 2):
        kms = KMeans(n_clusters=curr_clust, init='k-means++', random_state=42)
        kms = kms.fit(vector_norm)
        pred_labels = kms.labels_
        sil = silhouette_score(vectors, pred_labels)
        sils[curr_clust] = sil
        temp_labels[curr_clust] = pred_labels
        print(sil)
        best_n = max(sils, key=lambda x: sils[x])
        return temp_labels[best_n]

    # Agglomerative
    def agglomerative(self, vectors, n_clusters, method='ward', metric='cosine'):
        linkage_matrix = fastcluster.linkage(vectors, method=method, metric=metric)
        write_linkage_matrix(self.config, linkage_matrix)
        pred_labels = scipy.cluster.hierarchy.fcluster(linkage_matrix, n_clusters, criterion='maxclust')

        return pred_labels

    @property
    def pred_labels(self):
        return self._pred_labels
