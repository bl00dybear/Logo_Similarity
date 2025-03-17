# Logo_Similarity


## Table of Contents

| Section         |
|----------------|
| [Reasearch](#reasearch) |
| [Project Stucture](#project-structure) | 
| [Logo extraction](#logo-extraction) | 
| [Feature extraction](#features-extraction)|
| [Clustering](#clustering)|





## Reasearch

In the begining I had to identify the general type of the task. The answer is `Image Clustering`, more precisely image clustering on an unknown number of clusters. 

My first approach was to 
## Project structure

```txt
logo_similarity/
    │──scripts/
    │    │── main.py                     
    │    │── logo_extractor.py           
    │    │── feature_extractor.py        
    │    │── clustering.py               
    │    │── visualization.py           
    │    │──                  
    │──dataset.csv                
    │──embeddings.npy
    │──logo_dict.csv
    │──logos.snappy.parquet
    │──snappy_parquet_to_csv.py
    │──logos/
    │──results/

```

## Logo extraction
### JSON_ld
```html
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Example Company",
    "url": "https://example.com",
    "logo": {
        "url": "https://example.com/logo.png"
    }
}
</script>
```
### Logos found with first searching algorithm : 1163/4384

### Had this error:
```text
Error at https://bakertilly.ci: cannot identify image file <_io.BytesIO object at 0x753b3039a430>
```
The approach was to access this site and search for the logo. There I realized that the logo format is SVG, format unaccepted by: `PIL.Image.open(BytesIO(img_response.content))`. The solution is to download the logo as SVG and convert it to PNG (due to possibility of transparent background).


## Features extraction

## Clustering






```text
2631/4384
```

```text
adaptive background in feature extractor
```