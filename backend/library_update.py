import pandas as pd
import feedparser
from bs4 import BeautifulSoup
import requests
import backend.general_methods as gm


def library_update():
    """
    Updates the internal metadata library on govdata using an RSS feed to retrieve datasets available in CSV format.

    The function fetches the latest thirty datasets (due to technical limitations on govdata) from the open data portal
    govdata, extracts relevant metadata such as title, authors, description, link to the CSV file, tags, and keywords,
    and stores this information in a DataFrame. It also extracts the metadata of the CSV files, such as attributes and
    their data types, and cleanses the data of erroneous retrievals. Finally, the new records are added to the JSON file
    that serves as the library, removing any duplicates.

    Steps:
    ------
    1. Fetch the latest thirty datasets from the govdata RSS feed.
    2. Extract metadata from each dataset entry.
    3. Store extracted metadata in a DataFrame.
    4. Retrieve and clean metadata of the CSV files.
    5. Update the JSON library file with new records, removing duplicates.

    Returns:
    -------
    None
    """

    # RSS feed URL for CSV format open data on govdata
    rss_url = "https://www.govdata.de/web/guest/suchen/-/atomfeed/f/format%3Acsv%2Ctype%3Adataset%2C/s/lastmodification_desc"

    feed = feedparser.parse(rss_url)

    # Initialize lists to store metadata
    ids = []
    titles = []
    authors = []
    contents = []
    tag = []
    keywords = []

    for entry in feed.entries:

        try:
            # Fetch the HTML content of the dataset detail page
            response = requests.get(entry.get("id", ""))
            soup = BeautifulSoup(response.content, "html.parser")
            csv_link = gm.extract_csv_link(soup)
            kw = gm.extract_keywords(soup)

        except requests.RequestException as e:
            print(f"Error fetching the url: {e}")

        # Append extracted metadata to lists
        ids.append(csv_link)
        titles.append(entry.get("title", ""))
        authors.append(entry.get("author", ""))
        contents.append(entry.get("summary", ""))
        try:
            tag.append(entry.get("tags", "")[0]["label"])
        except IndexError:
            tag.append("No Tag")
        keywords.append(kw)

    # Create a DataFrame from the metadata lists, forming the data catalogue
    df = pd.DataFrame(
        {
            "Title": titles,
            "Author": authors,
            "Content": contents,
            "CSV": ids,
            "Tag": tag,
            "Keywords": keywords,
        }
    )

    # Initialize lists to store column types and top ten rows of each CSV
    c_type_list = []
    top_ten_list = []

    for i in range(len(df)):
        try:
            # Retrieve the CSV dataset
            odata = gm.get_govdata_dataset(df.loc[i, "CSV"])

        except:
            c_type_list.append("NA")
            top_ten_list.append("NA")
            continue

        # Check for bad data to keep the data catalogue in good shape
        if "Unnamed: 1" in odata.columns and "Unnamed: 2" in odata.columns:
            df.drop(i, axis=0, inplace=True)
        elif len(dict(odata.dtypes)) > 1:
            c_type_list.append(dict(odata.dtypes))
            top_ten_list.append(odata.iloc[:10].to_string())
        else:
            c_type_list.append("NA")
            top_ten_list.append("NA")

    # Add column types and top ten rows to the data catalogue
    df["Col_and_typ"] = c_type_list
    df["top_ten_cols"] = top_ten_list
    df = df.reset_index(drop=True)

    # Load the existing data catalogue and combine it with the new records, remove duplicates
    full_data = pd.read_json(
        "Lib/data_library.json",
    )

    full_data_ext = pd.concat([full_data, df], ignore_index=True).drop_duplicates(
        "Title"
    )
    full_data_ext = full_data_ext.loc[full_data_ext["top_ten_cols"] != "NA"]

    # The updated data catalogue is saved to the JSON file
    full_data_ext.to_json(
        "Lib/data_library.json", default_handler=str, orient="records", indent=4
    )
