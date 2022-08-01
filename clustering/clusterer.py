from kneed import KneeLocator
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.cluster import AffinityPropagation
from sklearn.metrics import silhouette_score
import hdbscan
from const import *

from sklearn import preprocessing

from scipy.cluster.vq import vq

import fastcluster
import scipy.cluster
import numpy as np

from write.writer import write_linkage_matrix


class Clusterer:

    def __init__(self, log, config):
        # properties
        self.log = log
        self.config = config
        self._pred_labels = None
        self.elbow = None

    def cluster(self, vectors, n_clusters=50):
        print("Start clustering " + str(len(vectors)) + " data points")
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
            self._pred_labels = self.agglomerative(vectors, n_clusters)
        elif self.config.clust == 'h_dbscan':
            self._pred_labels = self.h_dbscan(vectors, n_clusters)
        elif self.config.clust == 'affinity':
            self._pred_labels = self.affinity(vectors)
        elif self.config.clust == 'dbscan':
            self._pred_labels = self.dbscan(vectors, n_clusters)

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
        wcss = dict()
        temp_labels = dict()
        for curr_clust in range(int(len(self.log.pd_fv[XES_NAME_DF].unique()) * .5), int(len(self.log.pd_log[XES_NAME].unique()) * 1.5), 2):#in [12]:
            kms = KMeans(n_clusters=curr_clust, init='k-means++', random_state=42, algorithm="elkan")
            kms = kms.fit(vector_norm)
            pred_labels = kms.labels_
            sil = silhouette_score(vectors, pred_labels)
            sils[curr_clust] = sil
            wcss[curr_clust] = kms.inertia_
            temp_labels[curr_clust] = pred_labels
            print(sil)
            print(set(pred_labels))
            # break  # TODO
        best_n = max(sils, key=lambda x: sils[x])
        print(best_n)
        print(wcss)
        if len(wcss) > 1:
            kneedle = KneeLocator(list(wcss.keys()), list(wcss.values()), S=1.0, curve='convex', direction='decreasing')
            try:
                print(round(kneedle.knee, 3))
                self.elbow = round(kneedle.knee, 3)
            except TypeError:
                self.elbow = best_n
        else:
            self.elbow = best_n
        if self.config.multi_clustering:
            return temp_labels
        return temp_labels[best_n]

    # Agglomerative
    def agglomerative(self, vectors, n_clusters, method='ward'):
        linkage_matrix = fastcluster.linkage(vectors, method=method, metric=self.config.sim_metric)
        write_linkage_matrix(self.config, linkage_matrix)
        pred_labels = scipy.cluster.hierarchy.fcluster(linkage_matrix, n_clusters, criterion='maxclust')

        return pred_labels

    def h_dbscan(self, vectors, min_members):
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_members, min_samples=2)
        clusterer.fit(vectors)
        clusterer.condensed_tree_.plot()
        print("Number of clusters found by HDBSCAN", clusterer.labels_.max())
        return clusterer.labels_

    def dbscan(self, vectors, n_clusters):
        clusterer = DBSCAN(eps=3, min_samples=2).fit(vectors)
        return clusterer.labels_

    def affinity(self, vectors):
        clustering = AffinityPropagation(random_state=5).fit(vectors)
        return clustering.labels_

    @property
    def pred_labels(self):
        return self._pred_labels
