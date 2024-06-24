import ollama
import pandas as pd
import re


def mistral_retriever(full_data: pd.DataFrame, user_dataset: pd.DataFrame) -> dict:
    """
    Retrieves a matching dataset from the data catalog and identifies join variables for integration with the user dataset.

    Parameters:
    ----------
    full_data : pd.DataFrame
        The data catalog containing multiple datasets.
    user_dataset : pd.DataFrame
        The user-provided dataset.

    Returns:
    -------
    dict
        A dictionary containing the ID of the matching dataset and the join variables for both the matching and user datasets.
        The dictionary has the following keys:
        - 'dataset_id': The ID of the matching dataset.
        - 'col_name_user': The column name in the user dataset for joining.
        - 'col_name_catalog': The column name in the catalog dataset for joining.

        Returns None if no matching dataset is found.
    """

    # Construct a string representation of the first 10 rows of each of the first 5 datasets in the data catalog
    data_catalog = ""
    for index, row in full_data.loc[:5].iterrows():

        data_catalog += f'Dataset {index}:\n{row["top_ten_cols"]}\n\n'

    # Prepare the prompts for thechat interaction with the LLM
    # system defines the boundaries and task of the LLM, the user role prompts with the dataset
    messages = [
        {
            "role": "system",
            "content": f"""You are an AI model working in the backend of a software tool that integrates datasets. You get the first 10 rows of a dataset from the user and the first 10 rows of a number of datasets from the data catalog. Your ONE AND ONLY TAKS is to determine which single dataset from the data catalogue can be joined to the user dataset and on which column. 
        
        Data Catalog:
        {data_catalog}

        ALWAYS AND ONLY SEARCH IN THE CATALOG FOR A MATCHING DATAFRAME!
        As you are in the backend and your output will be the input to a python function, so ALWAYS answer according to the following scheme:
        "Dataset: [ID-Number of the catalog dataset], columns to join: [column name in user ds] - [column name in catalog dataset]"
        If you can't find a matching dataset in the catalog, please answer with "0"

        DO NOT write anything beyond the ID-Number of the dataset and the name of the column as specified in the scheme above. This would be a waste of your time and precious resources. A python function takes care of the rest and just splits your string into these two parts so no one cares about anything beyond the scheme "Dataset: [ID-Number of the catalog dataset], column to join: [column name in user ds] - [column name in catalog dataset]"
        Pay extra care to write down the EXACT column names as precision is EXTREMELY important for the later join to work. 
        """,
        },
        {
            "role": "user",
            "content": f"{user_dataset.iloc[:10].to_string()}?",
        },
    ]

    # The interaction is set up and executed with a MistralAI Model through ollama
    response = ollama.chat(model="mistral:7b-instruct-v0.3-q4_0", messages=messages)

    # Define the regex pattern to extract the important information from the model's response
    pattern = r"Dataset: (\d+), columns to join: (\w+) - (\w+)"

    # Search for the pattern in the response
    match = re.search(pattern, response["message"]["content"])

    if match:
        # If a match is found, return the extracted information as a dictionary
        return {
            "dataset_id": int(match.group(1)),
            "col_name_user": match.group(2),
            "col_name_catalog": match.group(3),
        }

    else:
        # If no match is found, return None, an error is created then
        return None
