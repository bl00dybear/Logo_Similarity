from logo_extractor import LogoExtractor

if __name__ == "__main__":
    logo_extractor = LogoExtractor(output_dir="../logos")
    logo_extractor.extract_from_csv(csv_file_path="../dataset.csv",domain_column="domain")