import numpy as np

from logo_extractor import LogoExtractor
from feature_extractor import FeatureExtractor
from clustering import LogoClustering
from cluster_visualization import *
from utils import *

if __name__ == "__main__":
    print("Do you want to search again for logos? [y/n]")
    response = input()
    logo_dict = {}
    if response == "y":
        logo_extractor = LogoExtractor(output_dir="../logos")
        logo_dict = logo_extractor.extract_from_csv(csv_file_path="../dataset.csv",domain_column="domain")
        write_dict_in_csv_file(logo_dict)

    print("Do you want to extract features? If you updated logo dataset, feature extraction is required! [y/n]")
    response = input()
    if response == "y":
        feature_extractor = FeatureExtractor(model_name="resnet50")

        print("\nExtracting features...\n")
        # print(logo_dict)

        extracted_features_num=0
        embeddings = []
        valid_domains = []
        if not logo_dict:
            logo_dict = read_dict_from_csv()
    #
    #     # print(logo_dict)
        for domain,values in logo_dict.items():
            if values[0]:
                features = feature_extractor.extract_features(values[0])
                extracted_features_num += 1
                print(f"Features extracted for {extracted_features_num}/{len(logo_dict)} domains")
                if features is not None:
                    for i in range(int(values[1])):
                        embeddings.append(features)
                    valid_domains.append(domain)

        embeddings = np.vstack(embeddings)
        print("Embeddings shape: ", embeddings.shape)
        np.save("../embeddings.npy", embeddings)
        print("Embeddings saved in ../embeddings.npy")

    embeddings = np.load("../embeddings.npy")
    # print(embeddings.shape)

    clusterer = LogoClustering(min_samples=3)
    labels = clusterer.perform_clustering(embeddings)

    print(labels)

    # plot_cluster_distribution_without_outliers(embeddings, labels)
    plot_cluster_distribution_without_outliers(embeddings, labels)

# tsme visualization w/o outliers 1 --> min samples 5
# tsme visualization w/o outliers 2 --> min samples 4
# tsme visualization w/o outliers 3 --> min samples 3
# tsme visualization w/o outliers 4 --> min samples 2