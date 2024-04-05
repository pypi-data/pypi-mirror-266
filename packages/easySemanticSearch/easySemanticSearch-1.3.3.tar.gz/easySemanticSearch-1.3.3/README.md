# Python Package - easySemanticSearch

## Overview

This Python package provides utilities for quick, simple and efficient semantic search.
This package leverages the SBERT capabilities of the SentenceTransformer. It allows users to perform semantic search on CSV files and pandas DataFrames.

Getting started is incredibly easy, just input the "CSV file path"/ "dataframe" and the query.
Advanced configurations are also possible, this can be achieved by inputting the correct arguments, a detailed guide is provided below.

The first run takes longer as the NLU model is downloaded and the dataset is encoded and embedded. Subsequent runs will take less than a second even for large dataset comprising of 19,000 records.

This package has been tested on a power restricted i7-4720hq (2015) running at 15 watts locked to ensure it will run on the majority of systems today with the best efficiency possible.


## Release Notes

### Version 1.3.3
- Multi-Threaded and Asynchronous processing of chunks has been added to reduce processing times upto 30 percentage on a power restricted i7-4720hq (2015) running at 15 watts locked.
- Enhanced output format - The result is now a List of Tuples where each Tuple consists of the result in JSON format output as a String. The Similarity scores still remain as Float.
- The Semantic Search has undergone further optimizations as a result of optimizing the input which is now a string passed with JSON style formatting instead of just String.

### Version 1.3.2
- The first public release of easySemanticSearch
- There are 2 methods of input, csv or dataframe.
- The output is a list of Tuples, each Tuple consists of the response in Str format and a Similarity Score in Float format.
- The initial processing times for 19000 records in a Job posting dataset (file size 97mb) take 47 minutes to encode with the default NLU model.
- After the initial embedding, the subsequent retrievals take less than 2 seconds on most accounts.
- If the embeddings are loaded into python and reused, it takes less than 1 second.


## Installation

You can install the package using pip:

```bash
pip install easySemanticSearch
```

## Methods

### csv_SimpleSemanticSearch

Performs semantic search on a CSV file and returns a list of results.

```python
from easySemanticSearch import csv_SimpleSemanticSearch

results = csv_SimpleSemanticSearch(csv_filepath_name, input_query="Your query")
```

#### Parameters:

- **csv_filepath_name** (str): Path to the CSV file.
- **input_query** (str, default="Some text"): Query to search for.
- **max_results** (int, default=5): Maximum number of results to return.
- **model_name** (str, default="all-MiniLM-L6-v2"): Name of the SentenceTransformer model to use.
- **embeddings_Filename** (str, default="embeddings_SemanticSearch.pkl"): Filename to save/load embeddings.
- **cache_folder** (str, default="default_folder"): Folder path to cache the model.

### dF_SimpleSemanticSearch

Performs semantic search on a pandas DataFrame and returns a list of results.

```python
from easySemanticSearch import dF_SimpleSemanticSearch
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'column1': ['text1', 'text2'],
    'column2': ['text3', 'text4']
})

results = dF_SimpleSemanticSearch(user_dataframe=df, input_query="The 1st text", max_results=5, model_name="all-MiniLM-L6-v2", embeddings_Filename="embeddings_SemanticSearch.pkl", cache_folder="C:\anonymous\BestSearcher\easySemanticSearch")
```

#### Parameters:

- **user_dataframe** (pd.DataFrame): Input pandas DataFrame.
- **input_query** (str, default="Some text"): Query to search for.
- **max_results** (int, default=5): Maximum number of results to return.
- **model_name** (str, default="all-MiniLM-L6-v2"): Name of the SentenceTransformer model to use.
- **embeddings_Filename** (str, default="embeddings_SemanticSearch.pkl"): Filename to save/load embeddings.
- **cache_folder** (str, default="default_folder"): Folder path to cache the model.

## Example Usage

1. Below is an example of how to Semantically search csv files using the `csv_SimpleSemanticSearch` method:

```python
#Import the libraries.
from easySemanticSearch import csv_SimpleSemanticSearch
import pandas as pd

# Read dataset from CSV file
csv_filepath_name = "CustomerService_logs.csv"

# Set input query
input_query = "I've experienced some crashes during busy times. Is there a plan to handle increased traffic or peak usage periods?"
print("Query:\n" + input_query + "\n\n")

# Get top 3 similar descriptions
max_results = 3    # The maximum number of search results to be retrieved.
top_SearchResults = csv_SimpleSemanticSearch(csv_filepath_name, input_query, max_results=max_results)

print("Knowledge Base:\n")
knowledgeBase = ""
for description, score in top_SearchResults:
    knowledgeBase = knowledgeBase + "\n" + description
    print(f"Search Results: {description}")
    print("-" * 25)
```


2. Below is an example of how to Semantically Search dataframes using the `dF_SimpleSemanticSearch` method:

```python
#Import the libraries.
from easySemanticSearch import dF_SimpleSemanticSearch
import pandas as pd


# Read dataset from CSV file
csv_filepath_name = "CustomerService_logs.csv"
sample_dataset = pd.DataFrame()
sample_dataset = pd.read_csv(csv_filepath_name)

# Set input query
input_query = "I've experienced some crashes during busy times. Is there a plan to handle increased traffic or peak usage periods?"
print("Query:\n" + input_query + "\n\n")

# Get top 3 similar descriptions
max_results = 3    # The maximum number of search results to be retrieved.
top_SearchResults = dF_SimpleSemanticSearch(sample_dataset, input_query, max_results=max_results)

print("Knowledge Base:\n")
knowledgeBase = ""
for description, score in top_SearchResults:
    knowledgeBase = knowledgeBase + "\n" + description
    print(f"Search Results: {description}")
    print("-" * 25)
```

## Note

The first time this code is run on a dataset, the encoding is time-consuming. Performance improves dramatically after the first initialization.
By default, the SentenceTransformer model used is "all-MiniLM-L6-v2", which can be changed based on user preference.