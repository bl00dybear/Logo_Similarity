import hdbscan

class LogoClustering:
    def __init__(self,eps=0.5,min_samples=5):
        self.eps = eps
        self.min_samples = min_samples

    def perform_clustering(self, embeddings):
        clusterer = hdbscan.HDBSCAN(metric="euclidean", min_cluster_size=self.min_samples)
        labels = clusterer.fit_predict(embeddings)
        return labels