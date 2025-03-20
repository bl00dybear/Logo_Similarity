import hdbscan

class LogoClustering:
    def __init__(self,min_clusters=3,min_samples=4):
        self.min_samples = min_samples
        self.min_clusters = min_clusters

    def perform_clustering(self, embeddings):
        # cosine distance is a good alternative but embeddings requires normalization (<1) and
            #also implementation
        # in Euclidean dist normalization is not required
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_clusters,
            min_samples=self.min_samples,
            metric="euclidean",
            cluster_selection_epsilon=0.15)
        # min_cluster size
        # scope: minimum size of a cluster (defines how many points are needed to form a cluster)
        # effect : if a group of points is smaller than this value, then it will not be considered
            # a valid cluster and will be labeled as an outlier or isolated point.

        # min samples
        # scope : the minimum density required for a point to be considered part of a cluster
        # effect : if min_samples is large, points that are marginal or slightly separated may
            # be excluded from the clusters and considered outliers. If it is small, then the
            # algorithm will accept a smaller number of points as part of a cluster.

        labels = clusterer.fit_predict(embeddings)
        return labels