import matplotlib.pyplot as plt
import os

from sklearn.manifold import TSNE


def plot_cluster_distribution(embeddings, labels, output_image="../results/tsne_visualization.png"):
    if len(embeddings) == 0:
        print("There are no embeddings to plot!")
        return

    os.makedirs("../results", exist_ok=True)

    tsne = TSNE(n_components=2, perplexity=30, random_state=42)

    reduced_features = tsne.fit_transform(embeddings)

    plt.figure(figsize=(10, 7))
    plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=labels, cmap="viridis", alpha=0.7)
    plt.colorbar(label="Cluster ID")
    plt.title("t-SNE Visualization of Clustering")
    plt.savefig(output_image)
    plt.show()

    print(f"Cluster visualization saved in {output_image}")


def plot_cluster_distribution_without_outliers(embeddings, labels, output_image="../results/tsne_visualization_without_outliers.png"):
    if len(embeddings) == 0:
        print("There are no embeddings to plot!")
        return

    os.makedirs("../results", exist_ok=True)

    valid_indices = labels != -1
    filtered_embeddings = embeddings[valid_indices]
    filtered_labels = labels[valid_indices]

    if len(filtered_embeddings) == 0:
        print("There are no data left after removing outliers!")
        return

    tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    reduced_features = tsne.fit_transform(filtered_embeddings)

    plt.figure(figsize=(10, 7))
    plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=filtered_labels, cmap="viridis", alpha=0.7)
    plt.colorbar(label="Cluster ID")
    plt.title("t-SNE Visualization of Clustering (Without Outliers)")
    plt.savefig(output_image)
    plt.show()

    print(f"Cluster visualization is save in {output_image}")

