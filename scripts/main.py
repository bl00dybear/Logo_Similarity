import numpy as np

from logo_extractor import LogoExtractor
from feature_extractor import FeatureExtractor
from clustering import LogoClustering
from cluster_visualization import *
from utils import *

if __name__ == "__main__":

    response = input("Do you want to search for logos? [y/n] ")

    while response not in ["y", "n"]:
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")
        response = input("Do you want to search for logos? [y/n] ")

    logo_dict = {}
    if response == "y":
        logo_extractor = LogoExtractor(output_dir="../logos")
        # what dose extract_from_csv: method that takes each domain from dataset and searches for logos
            # if the logo is found, it is downloaded in '../logos/' directory
        # returns: a dictionary that has domain as key and as value the path of the logo
        logo_dict = logo_extractor.extract_from_csv(csv_file_path="../datasets/dataset.csv", domain_column="domain")
        write_dict_in_csv_file(logo_dict)


    response = input("Do you want to extract features? If you updated logo dataset, feature extraction is required! [y/n] ")

    while response not in ["y", "n"]:
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")
        response = input("Do you want to extract features? [y/n] ")

    valid_domains = []
    if response == "y":
        feature_extractor = FeatureExtractor(model_name="resnet50")

        print("\nExtracting features...\n")

        extracted_features_num=0
        embeddings = []

        if not logo_dict:
            logo_dict = read_dict_from_csv()

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
        np.save("../datasets/embeddings.npy", embeddings)
        save_strings_to_csv(valid_domains,"../datasets/valid_domains.csv")
        print("Embeddings saved in ../datasets/embeddings.npy")

    embeddings = np.load("../datasets/embeddings.npy")

    clusterer = LogoClustering(min_clusters=2, min_samples=2)
    labels = clusterer.perform_clustering(embeddings)

    # print(len(labels))

    # plot_cluster_distribution_without_outliers(embeddings, labels)
    plot_cluster_distribution_without_outliers(embeddings, labels)
    # tsme visualization w/o outliers 1 --> min samples 5
    # tsme visualization w/o outliers 2 --> min samples 4
    # tsme visualization w/o outliers 3 --> min samples 3
    # tsme visualization w/o outliers 4 --> min samples 2

    if len(valid_domains):
        if not logo_dict:
            logo_dict = read_dict_from_csv()
        label_domain_dict = construct_label_domain_dict(labels, logo_dict, valid_domains)
    else:
        if not logo_dict:
            logo_dict = read_dict_from_csv()
        valid_domains = load_strings_from_csv("../datasets/valid_domains.csv")
        label_domain_dict = construct_label_domain_dict(labels, logo_dict, valid_domains)

    save_label_domain_dict(label_domain_dict)

