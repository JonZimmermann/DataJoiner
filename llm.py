import ollama
import pandas as pd

user_dataset = pd.read_csv("test_set.csv", encoding="iso-8859-1", sep=";")

full_data = pd.read_json(
    "Lib/data_library.json",
)

data_catalog = ""
for index, row in full_data.loc[:5].iterrows():

    data_catalog += f'Dataset {index}:\n{row["top_ten_cols"]}\n\n'

messages = [
    {
        "role": "system",
        "content": f"""You are an AI model working in the backend of a software tool that integrates datasets. You get the first 10 rows of a dataset from the user and the first 10 rows of a number of datasets from a data catalog. Your ONE AND ONLY TAKS is to determine which dataset from the data catalogue can be joined to the user dataset and on which column. 
        
        Data Catalog:
        {data_catalog}

        As you are in the backend and your output will be the input to a python function, so ALWAYS answer according to the following scheme:
        "Dataset: [ID-Number of the dataset], column to join: [column_name]"
        If you can't find a matching dataset, please answer with "0"

        DO NOT write anything beyond the ID-Number of the dataset and the name of the column as specified in the scheme above. This would be a waste of your time and precious resources. A python function takes care of the rest and just splits your string into these two parts so no one cares about anything beyond the scheme "Dataset: [ID-Number of the dataset], column to join: [column_name]"
        """,
    },
    {
        "role": "user",
        "content": f"{user_dataset.iloc[:10].to_string()}?",
    },
]

response = ollama.chat(model="mistral:7b-instruct-v0.3-q4_0", messages=messages)
print(response["message"]["content"])
