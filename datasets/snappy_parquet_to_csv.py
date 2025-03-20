import pandas as pd

file_path = "logos.snappy.parquet"

df = pd.read_parquet(file_path, engine="pyarrow")

# print(df.head())

df.to_csv("dataset.csv", index=False)
