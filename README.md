# Logo_Similarity


## Table of Contents

| Section                                                        |
|----------------------------------------------------------------|
| [Clone](#clone)                                                |
| [Reasearch](#reasearch)                                        |
| [Project Stucture](#project-structure)                         | 
| [Logo extraction](#logo-extraction)                            | 
| [Feature extraction](#features-extraction)                     |
| [Clustering](#clustering)                                      |
| [How to use CLI](#how-to-use-cli)                              |
| [Bug](#bug)                                                    |
| [How could I have improved it?](#how-could-i-have-improved-it) |


## Clone

### Considering that I made the project on Ubuntu, these are the steps to configure and run the project
Clone repository:
```bash
git clone git@github.com:bl00dybear/Logo_Similarity.git
```
Create the virtual environment:
```bash
python3 -m venv venv
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
[Back at Table of Contents](#table-of-contents)
## Reasearch

**In the begining I had to identify the general type of the task. The answer is `Image Clustering`, more precisely image clustering on an unknown number of clusters.** 

After an initial research, I found the `Feature-based Matching` method, which is a technique that identifies key points in images and matches them based on their distinctive features. However, the issue with this approach was the `execution time`, which was very `high`, making it unsuitable for larger datasets.

So, I didn’t stop at this idea and found a more robust approach: `clustering based on CNN embeddings`. Specifically, I used embeddings from the `penultimate layer` of the CNN, which captures high-level feature representations of the input data before the final classification layer. This layer encodes abstract patterns and semantic information, making it suitable for clustering similar instances more effectively.

**Now comes the question of how to implement the CNN. Do I have a large enough dataset for a CNN? Considering that I don't have this dataset, what should I do?**

The answer to all these questions is the use of a `pre-trained CNN model`, specifically `ResNet50`. I chose this model over `InceptionV3` (another good pretrained CNN model) because it is more `widely used`, performs better on `large datasets`, and its residual connections allow for more `effective training` of deeper networks.

Is `ResNet50` scalable?<br>
`ResNet50` is scalable because its deep architecture with residual connections handles large datasets well, it can be optimized with transfer learning to reduce computational requirements, and it leverages GPU resources efficiently for faster training on extensive data.

How do I do clustering with these embeddings?<br>
After extracting the embeddings, I should performed clustering using `HDBSCAN` (better than `DBSCAN` because it handles varying densities better). At the same time, it is quite suitable for logos because it effectively separates outliers, focusing more on forming correct clusters rather than forcing a logo into a specific cluster. Additionally, I couldn't use `K-Means` due to the unknown number of clusters.

After forming this overview of how I should code this project, I got to work. The following are 3 sections, covering the three main parts of the project, where I will present more technically how I coded them and some of the issues I encountered.

[Back at Table of Contents](#table-of-contents)


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
    │──datasets/
    │    │── dataset.csv               # initial list of doamins
    │    │── embedddings.npy           # data after feature extraction 
    │    │── label_domain_disct.json   # final output of the program
    │    │── logo_dict.cvs             # contains domain, path to downloaded logo, and num of appears of the domain in dataset
    │    │── logos.snappy.parquet      
    │    │── snappy_parquet_to_csv.py  # converter to be abel to read the dataset I received
    │    │── valid_domains.csv         # an array with domains name whose logo was found
    │    │── best_parameters.json      # best params for hdbscan and metrics for clustering algorithm
    │──logos/                          # directory with logos downloaded
    │──results/                        # directory with numerous plots made during development
    |──requirements.txt                # file used to configure venv on any device with same packages I used

```
[Back at Table of Contents](#table-of-contents)

## **Logo extraction**

I started by fetching the webpage HTML with requests and using `BeautifulSoup` to parse it. First, the algorithm tries to find logos in the `JSON-LD` metadata (an example below). If that didn’t work, it looks for `<img>` tags in attributes like `class`, `id`, `alt`, and `src`. This search took longer but usually worked better. I have also to normalized image URLs, especially if they were relative, to ensure they pointed to the correct location. The algorithm handles different image formats, such as converting `SVG` files to `PNG` and saving `Base64-encoded images` also as `PNG`, particularly for `GIF` logos. Once the logo is found, I downloaded and saved it in the `~/logos` folder. To speedup this process I used multithreading rendering, so that 30 threads searches for logos at the same time.
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

### **Logos found for distinct domains with first searching algorithm : 1163/3416 (34%)**

### SVG/GIF error:
```text
Error at https://bakertilly.ci: cannot identify image file <_io.BytesIO object at 0x753b3039a430>
```
The approach was to access this site and search for the logo. There I realized that the logo format is SVG, format unaccepted by: `PIL.Image.open(BytesIO(img_response.content))`. The solution is to download the logo as SVG and convert it to PNG (due to possibility of transparent background). Later I realized that logos can also be GIFs, where I did exactly the same thing.

### Sites accessible only from real browsers
Another problem I encountered, which I couldn't solve, was that some websites couldn't be accessed by my code (but they worked in the browser). I even tried writing code that would mimic a real browser as much as possible. Since it didn't work at all, I assumed that those websites had firewalls and protections that I don't know how to bypass.

There were also websites that were unreachable even from the browser, for which I would most likely have needed a VPN.

### **Logos found for distinct domains with second searching algorithm : 2600/3416 (76%)**

[Back at Table of Contents](#table-of-contents)

## Features extraction

As I mentioned in the research section, I extract the embeddings by taking the penultimate layer before the output of the pre-trained `ResNet50` model. This approach is robust because the penultimate layer captures high-level features and abstract representations, which are less specific to the model's final decision, making them more generalizable for clustering.
### Adaptive background 
The only issue I encountered was with logos that have a transparent background, as I need to apply a background to them. To avoid adding a background that would influence the features too much, potentially favoring or disadvantaging a logo in the clustering decision, I considered that the most neutral approach would be to add a light background when the image's brightness is high, and a dark one otherwise.

[Back at Table of Contents](#table-of-contents)

## Clustering
The first version of the clustering code was a simple one where we just called `HDBSCAN` and processed the input and output parameters. As the form of verification for the entire program, I plotted the clusters in a `t-SNE` diagram (since the embedding size is 2048 dimensions), obtaining something where the clusters weren't very distinct due to outliers:

![](/results/tsne_visualization.png)
**So I also plotted it without the outliers:**
![](/results/tsne_visualization_without_outliers.png)

After seeing that fairly good clusters were formed visually (there are clear separations and no color intersections), I also generated the program's output, which is located in `~/datasets/label_domain_dict.json`. It contains a dictionary with the cluster ID as the key (with `-1` being the ID for outliers) and the corresponding domains for the cluster as the value in an array.

At the end of my output file i saw this:
```json lines
"296": [
        "flashbay.fr",
        "flashbay.hu"
    ],
"297": [
     "flashbay.pt",
     "flashbay.es"
    ],
"298": [
     "flashbay.ca"
    ],
"299": [
     "flashbay.com.my",
     "flashbay.co.nz"
    ]
```
And then I thought that the parameter adjustment I made was not the most optimal. At that moment, I considered it was time for a new feature regarding clustering: `automatic parameter adjustment`. I created another method within the class, totally inefficient (brute force), whose runs lasted about an hour but provided the most optimal parameters we could give to `HDBSCAN`. A fun fact is that this brute force approach came up with the same parameters I had in mind, but at least now we have them in the `~/datasets/best_parameters.json` file, along with the metrics for the entire clustering algorithm.

[Back at Table of Contents](#table-of-contents)
## How to use CLI?

I designed the program execution to be modular, meaning there are two checkpoints between the three parts of the program where data is saved in the helper folder ~/datasets. This facilitates its further development by reducing execution time. If updates are made to a module, the program needs to be run in a cascade (i.e., if we updated the web scraping part, we need to run the entire program, but if we only updated the clustering part, we don’t need to rerun the steps before clustering). Running the parameter balancing algorithm is advisable if there are major changes in the dataset (though I consider it unnecessary even then if the domain distribution remains the same).

[Back at Table of Contents](#table-of-contents)
## Bug

There is a bug that I am aware of but haven't had the chance to fix. If the extraction of a feature within the `ResNet50` model fails, there will be an index offset, and the output will be formed incorrectly, meaning the last domains of one cluster will be shifted to the next cluster.

[Back at Table of Contents](#table-of-contents)
## How could I have improved it?
The first improvement I could have made would have been to add the favicon as a backup for logo extraction (I hesitated to do this because the poor quality of the favicon and the possible difference in the logo might have confused me during development, as the clusters could have formed completely differently).

Another improvement would have been to explore the CNN model parameters further, even though I believe the improvement wouldn't have been substantial.

[Back at Table of Contents](#table-of-contents)
