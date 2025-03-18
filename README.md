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
    │    │── main.py                    # principal pipeline of the program    
    │    │── logo_extractor.py          # web scarping algorithm for logos
    │    │── feature_extractor.py       # pretrained cnn used for feature extraction    
    │    │── clustering.py              # hdbscan model used for clustering    
    │    │── cluster_visualization.py   # tsne visualization                
    │    │── utils.py                   # auxiliar functions used in main.py
    │──dataset.csv                      
    │──embeddings.npy
    │──logo_dict.csv
    │──logos.snappy.parquet
    │──snappy_parquet_to_csv.py
    │──logos/
    │──results/

```

## **Logo extraction**

The `LogoExtractor` class automates the process of retrieving website logos by:  

1. **Fetching webpage HTML** using `requests` and parsing it with `BeautifulSoup`.  
2. **Extracting logos** from multiple sources:  
   - **JSON-LD metadata** as a first approach.
```html
This is how a json_ld looks like:

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
   - **`<img>` tags** that may be included in `class`, `id`, `alt`, `src` tags (less efficient search but with a higher success rate).  
3. **Normalizing URLs** to ensure valid image links (needed in cases where image link is relative).  
4. **Handling different formats**:  
   - **SVG files** are converted to PNG.  
   - **Base64-encoded images** are decoded and saved (especially GIF logos).  
5. **Downloading and saving the logo** in the `../logos` directory.  
6. **Supporting bulk extraction** via CSV input, leveraging multithreading for efficiency.  


### **Logos found with first searching algorithm : 1163/4384**

### SVG/GIF error:
```text
Error at https://bakertilly.ci: cannot identify image file <_io.BytesIO object at 0x753b3039a430>
```
The approach was to access this site and search for the logo. There I realized that the logo format is SVG, format unaccepted by: `PIL.Image.open(BytesIO(img_response.content))`. The solution is to download the logo as SVG and convert it to PNG (due to possibility of transparent background). Later I realized that logos can also be GIFs, where I did exactly the same thing.

### Sites accessible only from real browsers



## Features extraction

## Clustering






```text
2631/4384
```

```text
adaptive background in feature extractor
```