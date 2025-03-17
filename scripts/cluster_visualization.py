import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import os


def plot_cluster_distribution(embeddings, labels, output_image="../results/tsne_visualization.png"):
    if len(embeddings) == 0:
        print("Nu există embeddings pentru vizualizare!")
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

    print(f"Vizualizarea clustering-ului salvată în {output_image}")