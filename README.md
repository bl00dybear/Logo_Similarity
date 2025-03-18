# Logo_Similarity


## Table of Contents

| Section         |
|----------------|
| [Clone](#clone)|
| [Reasearch](#reasearch) |
| [Project Stucture](#project-structure) | 
| [Logo extraction](#logo-extraction) | 
| [Feature extraction](#features-extraction)|
| [Clustering](#clustering)|



## Clone

### Considering that I made the project on Ubuntu, these are the steps to configure and run the project
Clone repository:
```bash
git clone git@github.com:bl00dybear/Logo_Similarity.git
```
Create the virtual environment:
```bash
python -m venv venv
```
Activate it on Linux:
```bash
source venv/bin/activate  
```
Activate it on Windows:
```bash
venv\Scripts\activate 
```
Install required packages:
```bash
pip install -r requirements.txt
```

## Reasearch

**In the begining I had to identify the general type of the task. The answer is `Image Clustering`, more precisely image clustering on an unknown number of clusters.** 

After an initial research, I found the `Feature-based Matching` method, which is a technique that identifies key points in images and matches them based on their distinctive features. However, the issue with this approach was the `execution time`, which was very `high`, making it unsuitable for larger datasets.

So, I didn’t stop at this idea and found a more robust approach: `clustering based on CNN embeddings`. Specifically, I used embeddings from the `penultimate layer` of the CNN, which captures high-level feature representations of the input data before the final classification layer. This layer encodes abstract patterns and semantic information, making it suitable for clustering similar instances more effectively.

**Now comes the question of how to implement the CNN. Do I have a large enough dataset for a CNN? Considering that I don't have this dataset, what should I do?**

The answer to all these questions is the use of a `pre-trained CNN model`, specifically `ResNet50`. I chose this model over `InceptionV3` (another good pretrained CNN model) because it is more `widely used`, performs better on `large datasets`, and its residual connections allow for more `effective training` of deeper networks.

Is `ResNet50` scalable?<br>
`ResNet50` is scalable because its deep architecture with residual connections handles large datasets well, it can be optimized with transfer learning to reduce computational requirements, and it leverages GPU resources efficiently for faster training on extensive data.
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

### Adaptive background 

## Clustering






