import numpy as np

from logo_extractor import LogoExtractor
from feature_extractor import FeatureExtractor
from utils import *

if __name__ == "__main__":
    print("Do you want to search again for logos? [y/n]")
    response = input()
    logo_dict = {}
    if response == "y":
        logo_extractor = LogoExtractor(output_dir="../logos")
        logo_dict = logo_extractor.extract_from_csv(csv_file_path="../dataset.csv",domain_column="domain")
        write_dict_in_csv_file(logo_dict)

    feature_extractor = FeatureExtractor(model_name="resnet50")

    embeddings = []
    valid_domains = []
    if not logo_dict:
        logo_dict = read_dict_from_csv()
    for domain,logo_path in logo_dict.items():
        if logo_path:
            features = feature_extractor.extract_features(logo_path)
            if features is not None:
                embeddings.append(features)
                valid_domains.append(domain)

    embeddings = np.vstack(embeddings)