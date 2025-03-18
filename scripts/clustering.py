import hdbscan

class LogoClustering:
    def __init__(self,min_samples=4):
        self.min_samples = min_samples

    def perform_clustering(self, embeddings):
        # cosine distance bud embeddings requires normalization (<1)
        # in euclidean dist normalization is not required
        clusterer = hdbscan.HDBSCAN(metric="euclidean", min_cluster_size=self.min_samples)
        labels = clusterer.fit_predict(embeddings)
        return labels