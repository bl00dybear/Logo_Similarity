import numpy as np

from logo_extractor import LogoExtractor
from scripts.feature_extractor import FeatureExtractor

if __name__ == "__main__":
    logo_extractor = LogoExtractor(output_dir="../logos")
    logo_dict = logo_extractor.extract_from_csv(csv_file_path="../dataset.csv",domain_column="domain")

    feature_extractor = FeatureExtractor(model_name="resnet50")

    embeddings = []
    valid_domains = []

    for domain,logo_path in logo_dict.items():
        if logo_path:
            features = feature_extractor.extract_features(logo_path)
            if features is not None:
                embeddings.append(features)
                valid_domains.append(domain)

    embeddings = np.vstack(embeddings)