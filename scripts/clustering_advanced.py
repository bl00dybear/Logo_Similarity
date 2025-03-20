import hdbscan
import numpy as np

from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances


class LogoClustering:
    def __init__(self, min_clusters=3, min_samples=4, metric="euclidean",
                 cluster_selection_epsilon=0.15, cluster_selection_method='eom'):

        self.min_clusters = min_clusters
        self.min_samples = min_samples
        self.metric = metric
        self.cluster_selection_epsilon = cluster_selection_epsilon
        self.cluster_selection_method = cluster_selection_method

    def _normalize_embeddings(self, embeddings):
        # cosine distance requires normalization
        if self.metric == "cosine":
            norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
            # avoiding /0
            norm[norm == 0] = 1e-10
            return embeddings / norm
        return embeddings

    def perform_clustering(self, embeddings):
        embeddings = np.asarray(embeddings, dtype=np.float64)

        # for cosine metric we have to calculate distance matrix
        if self.metric == "cosine":
            normalized_embeddings = self._normalize_embeddings(embeddings)
            distance_matrix = cosine_distances(normalized_embeddings)
            np.fill_diagonal(distance_matrix, 0)

            distance_matrix = np.asarray(distance_matrix, dtype=np.float64) # hdbscan needs float64 data type

            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_clusters,
                min_samples=self.min_samples,
                metric='precomputed',
                cluster_selection_epsilon=self.cluster_selection_epsilon,
                cluster_selection_method=self.cluster_selection_method
            )

            labels = clusterer.fit_predict(distance_matrix)
        else:
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_clusters,
                min_samples=self.min_samples,
                metric=self.metric,
                cluster_selection_epsilon=self.cluster_selection_epsilon,
                cluster_selection_method=self.cluster_selection_method
            )

            labels = clusterer.fit_predict(embeddings)

        return labels

    def find_optimal_parameters(self, embeddings):
        best_score = -1
        best_params = {}
        best_clusters = {}
        best_labels = None

        min_cluster_sizes = [2, 3, 5, 8, 10]
        min_samples_values = [2, 3, 4, 5]
        metrics = ["cosine", "euclidean"]
        epsilons = [0.1, 0.15, 0.2, 0.25]
        cluster_methods = ["eom", "leaf"]

        results = []
        cluster_index = 1

        for mcs in min_cluster_sizes:
            for ms in min_samples_values:
                for metric in metrics:
                    for eps in epsilons:
                        for method in cluster_methods:
                            self.min_clusters = mcs
                            self.min_samples = ms
                            self.metric = metric
                            self.cluster_selection_epsilon = eps
                            self.cluster_selection_method = method

                            print(f"Performing clustering no {cluster_index} / 320")
                            print("Parameters:")
                            print(f"Min-clusters: {mcs}")
                            print(f"Min-samples: {ms}")
                            print(f"Metric: {metric}")
                            print(f"Epsilon: {eps}")
                            print(f"Method: {method}")

                            cluster_index += 1
                            labels = self.perform_clustering(embeddings)

                            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                            n_outliers = np.sum(labels == -1)
                            outlier_percentage = n_outliers / len(labels) * 100

                            # silhouete score measures how well separated and well formed the clusters are
                                # is between -1 and 1, a higher score indicates well defined clusters
                            score = -1
                            if n_clusters >= 2:
                                mask = labels != -1 # exclude outliers
                                if sum(mask) > n_clusters:
                                    try:
                                        if metric == "cosine":
                                            normalized_emb = self._normalize_embeddings(embeddings[mask])
                                            score = silhouette_score(normalized_emb, labels[mask], metric='cosine')
                                        else:
                                            score = silhouette_score(embeddings[mask], labels[mask], metric=metric)
                                    except:
                                        pass

                            # composite score combines silhouette score with percentage of outliers
                                # if there are more than 30% of outliers we have to decrease this score
                                # the scope of this score is to balance clusters quality and numm of outliers
                            composite_score = score if score > 0 else 0
                            if outlier_percentage > 30:
                                composite_score *= (1 - (outlier_percentage - 30) / 100)

                            # this score prefers configs with more clusters over those with fewer but higher-quality clusters
                                #balance the trade-off between the number of clusters and their quality
                            cluster_weighted_score = composite_score * (0.7 + 0.3 * min(n_clusters, 10) / 10)

                            result = {
                                'min_clusters': mcs,
                                'min_samples': ms,
                                'metric': metric,
                                'epsilon': eps,
                                'method': method,
                                'n_clusters': n_clusters,
                                'n_outliers': n_outliers,
                                'outlier_percentage': outlier_percentage,
                                'silhouette': score,
                                'composite_score': composite_score,
                                'cluster_weighted_score': cluster_weighted_score
                            }
                            results.append(result)

                            if composite_score > best_score and n_clusters >= 2:
                                best_score = composite_score
                                best_params = result
                                best_labels = labels

        self.min_clusters = best_params['min_clusters']
        self.min_samples = best_params['min_samples']
        self.metric = best_params['metric']
        self.cluster_selection_epsilon = best_params['epsilon']
        self.cluster_selection_method = best_params['method']

        sorted_results = sorted(results, key=lambda x: x['composite_score'], reverse=True)
        top_results = sorted_results[:5]

        cluster_weighted_results = sorted(results, key=lambda x: x['cluster_weighted_score'], reverse=True)
        top_cluster_weighted = cluster_weighted_results[:5]


        return {
            'best_params': best_params,
            'best_score': best_score,
            'best_clusters': best_clusters,
            'best_labels': best_labels,
            'top_combinations': top_results,
            'top_cluster_weighted': top_cluster_weighted
            # 'labels': labels
        }