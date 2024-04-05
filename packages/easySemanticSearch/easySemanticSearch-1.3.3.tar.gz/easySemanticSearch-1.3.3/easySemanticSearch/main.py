# 1) Libraries for the Sentence transformers (SBERT) - These perform the embeddings and assist in the Semantic Searchability.
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import os   # Library to prevent or ignore warnings from being displayed.

# 2) Library to store and retrieve embeddings.
import pickle
from pathlib import Path  # Library for file path - used to check if file exists.

# 3) Libraries for processing the embeddings for better comprehension.
import json           # To convert the embeded and output data to dataframes.
import numpy as np    # To compute mean, etc for the embeddings
import pandas as pd    # For the dataframe that stores the embeddings.

# 4) Libraries to enable multcore processing for faster embeddings.
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
import psutil


# This is initialized as false to identify if the module has already been initialized, this improves performance after initial initialization.
is_model_initialized = False

#__________________________

def _load_csvDataset(csv_filepath_name):
    """
    Warning: Private method, NOT intended for use independently.
    Takes csv as Dataset and produces a pandas series output.
    The output combines all columns to 1 column.
    """

    # Read dataset from CSV file
    user_dataframe = pd.DataFrame()
    user_dataframe = pd.read_csv(csv_filepath_name)

    # Collating the values from all the other fields into a new field 'All_Data'.
    FullData_AllColumns = user_dataframe.apply(lambda row: json.dumps({col: str(row[col]) for col in user_dataframe.columns.tolist()}, indent=4), axis=1)

    # Returning the combined pd.series.
    return FullData_AllColumns

#__________________________
    
def _process_DataFrame(user_dataframe):
    """
    Warning: Private method, NOT intended for use independently.
    Takes a dataframe and produces a pandas series output.
    The output combines all columns to 1 column.
    """

    # Collating the values from all the other fields into a new field 'All_Data'.
    FullData_AllColumns = user_dataframe.apply(lambda row: json.dumps({col: str(row[col]) for col in user_dataframe.columns.tolist()}, indent=4), axis=1)

    # Returning the combined pd.series.
    return FullData_AllColumns

#__________________________

def _initiate_SemanticSearchModel(model_name, cache_folder):
    """
    Warning: Private method, NOT intended for use independently.
    This block of code initiated the SentenceTransformer model if not initiated.
    The default model used is "all-MiniLM-L6-v2".
    This is not fine tuned. Results may vary based on the dataset.
    """

    # Specify the local cache directory where the SentenceTransformer exists.
    # This is a Language Representation Model or a Language Model. It is used for NLU - Natural Language Understanding.
    # The all-mpnet-base-v2 model provides the best quality, while all-MiniLM-L6-v2 is 5 times faster and still offers good quality.
    LM_SentenceTransformer = model_name #"all-MiniLM-L6-v2" #"bert-base-uncased"  #"bert-base-nli-mean-tokens"    
    cache_folder = cache_folder

    # Set environment variable to disable symlinks warning
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

    # Initialize a different SentenceTransformer model
    model = SentenceTransformer(LM_SentenceTransformer, cache_folder=cache_folder)

    # Returning the model.
    return model


#__________________________

# Function to compute embeddings for a chunk of sentences
def _compute_embeddings(chunk):
    """
    Warning: Private method, NOT intended for use independently.
    This computes the embeddings.
    """
    return model.encode(chunk.tolist(), convert_to_tensor=True)


def _multicore_embeddingsEncoding(FullData_AllColumns):
    """
    Warning: Private method, NOT intended for use independently.
    Utilizes multi core processing to speed up encoding times.   
    """

    # Get the number of CPU cores
    num_cores = cpu_count()  # Limiting to 4 CPU cores

    # Get available memory
    available_memory_bytes = psutil.virtual_memory().available

    # Estimate embedding size
    embedding_size = model.get_sentence_embedding_dimension()

    # Convert pandas.Series to numpy array
    sentences = FullData_AllColumns.values

    # Compute the optimal chunk size based on available memory and dataset size
    total_sentences = len(sentences)

    # Estimate memory usage for embeddings of a single chunk
    optimal_memory_usage = available_memory_bytes / num_cores
    optimal_chunk_size = int(optimal_memory_usage / (embedding_size * 4))  # Assuming float32 for embeddings

    # Adjust chunk size to a smaller value, such as 10 or 20
    chunk_size = min(total_sentences/num_cores, optimal_chunk_size)  # Adjust this value based on trial and error

    # Split the dataset into chunks based on chunk size
    chunks = np.array_split(sentences, int(np.ceil(total_sentences / chunk_size)))

    # Initialize a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers= num_cores) as executor:
        embeddings_list = list(executor.map(_compute_embeddings, chunks))

    # Concatenate the embeddings
    embeddings = np.concatenate(embeddings_list, axis=0)

    # Return the encodings.
    return embeddings


#__________________________


def _embeddings_create_reuse(csv_filepath_name, embeddings_Filename, model):
    """
    Warning: Private method, NOT intended for use independently.
    The default name for embeddings is "embeddings_SemanticSearch.pkl".
    To create new embeddings, rename or delete existing one.
    """

    # Provide the file path and/or name, the extension should be .pkl. For example: "embeddings_sample.pkl"
    file_pathname = embeddings_Filename
    file_path = Path(file_pathname)

    if file_path.exists():
        # Load sentences & embeddings from storage
        with open(file_pathname, "rb") as fIn:
            stored_data = pickle.load(fIn)
            FullData_AllColumns = stored_data["sentences"]
            embeddings_FullData_AllColumns = stored_data["embeddings"]

    # Else create the embeddings.
    else:

        # if csv_filepath_name is string, we use the methods for csvDataset loading.
        if isinstance(csv_filepath_name, str):

            # Compute embeddings for the FullData_AllColumns column
            FullData_AllColumns = _load_csvDataset(csv_filepath_name)
            embeddings_FullData_AllColumns = _multicore_embeddingsEncoding(FullData_AllColumns = FullData_AllColumns)

            # Store sentences & embeddings on storage
            with open(file_pathname, "wb") as fOut:
                pickle.dump({"sentences": FullData_AllColumns, "embeddings": embeddings_FullData_AllColumns}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

        # Else - when csv_filepath_name is NOT str, we assume it is a DataFrame.
        else:

            # Compute embeddings for the FullData_AllColumns column
            FullData_AllColumns = _process_DataFrame(csv_filepath_name)
            embeddings_FullData_AllColumns = _multicore_embeddingsEncoding(FullData_AllColumns = FullData_AllColumns)

            # Store sentences & embeddings on storage
            with open(file_pathname, "wb") as fOut:
                pickle.dump({"sentences": FullData_AllColumns, "embeddings": embeddings_FullData_AllColumns}, fOut, protocol=pickle.HIGHEST_PROTOCOL)


    #Return the FullData_AllColumns, embeddings_FullData_AllColumns.
    return FullData_AllColumns, embeddings_FullData_AllColumns


#__________________________

def _get_top_semanticResults(query, data_embeddings, data_fromDataSet, model, top_k):
    """
    Warning: Private method, NOT intended for use independently.
    Fetches the top search results for the query.
    """

    # Encode the query
    query_embedding = model.encode([query], convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_scores = util.pytorch_cos_sim(query_embedding, data_embeddings)[0]
    
    # Sort the scores in decreasing order
    sorted_indices = np.argsort(-cosine_scores.cpu().numpy())
    
    # Retrieve top k descriptions
    top_results = [(data_fromDataSet[i], cosine_scores[i].item()) for i in sorted_indices[:top_k]]
    
    # Returning the top results.
    return top_results

#__________________________

def csv_SimpleSemanticSearch(csv_filepath_name, input_query = "Some text", max_results = 5, model_name = "all-MiniLM-L6-v2", embeddings_Filename = "embeddings_SemanticSearch.pkl", cache_folder = "default_folder"):
    """
    Takes (input_query, csv_filepath_name, max_results) as input and makes it queryable.
    First time encoding is time consuming. Performance improves after first time.
    The default SentenceTransformer model name from huggingface = "all-MiniLM-L6-v2", this can be changed.
    Please refer to the PyPi Package page for more detailed information.
    """

    # Global variable to check if the model is initialized
    global is_model_initialized, model, embeddings_FullData_AllColumns, FullData_AllColumns

    # If the model is already running and embeddgins are loaded.
    if is_model_initialized:

        # Fetch the Semantic Search Results.
        top_Searchresults = _get_top_semanticResults(data_embeddings = embeddings_FullData_AllColumns, data_fromDataSet = FullData_AllColumns, model = model, query = input_query, top_k = max_results)

    
    # If the model needs to be initialized.
    else:
        
        # If the cache_folder is set to "default", create the folder.
        if cache_folder == "default_folder":

            # Define the cache folder in the user's home directory
            cache_folder = cache_folder = Path.cwd() / ".cache" / "sentence_transformers"


        # Initializing the Semantic Search model.
        model = _initiate_SemanticSearchModel(model_name, cache_folder)
        is_model_initialized = True    # Setting this boolean to True, since the model is running now.

        FullData_AllColumns, embeddings_FullData_AllColumns = _embeddings_create_reuse(csv_filepath_name, embeddings_Filename, model = model)

        # Fetch the Semantic Search Results.
        top_Searchresults = _get_top_semanticResults(data_embeddings = embeddings_FullData_AllColumns, data_fromDataSet = FullData_AllColumns, model = model, query = input_query, top_k = max_results)

    
    # Return the search results.
    return top_Searchresults    
#__________________________

def df_SimpleSemanticSearch(user_dataframe, input_query = "Some text", max_results = 5, model_name = "all-MiniLM-L6-v2", embeddings_Filename = "embeddings_SemanticSearch.pkl", cache_folder = "default_folder"):
    """
    Takes (input_query, csv_filepath_name, max_results) as input and makes it queryable.
    First time encoding is time consuming. Performance improves after first time.
    The default SentenceTransformer model name from huggingface = "all-MiniLM-L6-v2", this can be changed.
    Please refer to the PyPi Package page for more detailed information.
    """

    # Global variable to check if the model is initialized
    global is_model_initialized, model, embeddings_FullData_AllColumns, FullData_AllColumns

    # If the model is already running and embeddgins are loaded.
    if is_model_initialized:

        # Fetch the Semantic Search Results.
        top_Searchresults = _get_top_semanticResults(data_embeddings = embeddings_FullData_AllColumns, data_fromDataSet = FullData_AllColumns, model = model, query = input_query, top_k = max_results)

    
    # If the model needs to be initialized.
    else:
        
        # If the cache_folder is set to "default", create the folder.
        if cache_folder == "default_folder":

            # Define the cache folder in the user's home directory
            cache_folder = cache_folder = Path.cwd() / ".cache" / "sentence_transformers"


        # Initializing the Semantic Search model.
        model = _initiate_SemanticSearchModel(model_name, cache_folder)
        is_model_initialized = True    # Setting this boolean to True, since the model is running now.

        FullData_AllColumns, embeddings_FullData_AllColumns = _embeddings_create_reuse(user_dataframe, embeddings_Filename, model = model)

        # Fetch the Semantic Search Results.
        top_Searchresults = _get_top_semanticResults(data_embeddings = embeddings_FullData_AllColumns, data_fromDataSet = FullData_AllColumns, model = model, query = input_query, top_k = max_results)

    
    # Return the search results.
    return top_Searchresults   

#__________________________
