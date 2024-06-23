import pandas as pd
import feedparser
from bs4 import BeautifulSoup
import io
import requests
import backend.general_methods as gm


# NEEDS Regular execution -> DONE
def library_update():
    """
    This function is used to regularly update the internal metadata library on govdata. The function uses an RSS feed to retrieve
    thirty datasets (restriction due to technical limitations on govdata) that are available in CSV format on the open data portal govdata.
    The title, authors, description, link to the CSV file, tag and available keywords are extracted and stored in a data frame.
    The CSV link is then used to extract the metadata of the CSV files, such as attributes and their data types.
    The data set is cleansed of erroneous retrievals resulting from incorrect data.
    Finally, the new records are added to the json file that serves as the library, and the library is also cleaned of duplicate
    records that have been retrieved.
    """
    # search for csv open data as RSS
    rss_url = "https://www.govdata.de/web/guest/suchen/-/atomfeed/f/format%3Acsv%2Ctype%3Adataset%2C/s/lastmodification_desc"

    feed = feedparser.parse(rss_url)

    ids = []
    titles = []
    authors = []
    contents = []
    tag = []
    keywords = []

    for entry in feed.entries:

        try:
            response = requests.get(entry.get("id", ""))
            soup = BeautifulSoup(response.content, "html.parser")
            csv_link = gm.extract_csv_link(soup)
            kw = gm.extract_keywords(soup)

        except requests.RequestException as e:
            print(f"Error fetching the url: {e}")

        ids.append(csv_link)
        titles.append(entry.get("title", ""))
        authors.append(entry.get("author", ""))
        contents.append(entry.get("summary", ""))
        try:
            tag.append(entry.get("tags", "")[0]["label"])
        except IndexError:
            tag.append("No Tag")
        keywords.append(kw)

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

    c_type_list = []
    top_ten_list = []

    for i in range(len(df)):
        try:
            odata = gm.get_govdata_dataset(df.loc[i, "CSV"])

        except:
            c_type_list.append("NA")
            top_ten_list.append("NA")
            continue

        if "Unnamed: 1" in odata.columns and "Unnamed: 2" in odata.columns:
            df.drop(i, axis=0, inplace=True)
        elif len(dict(odata.dtypes)) > 1:
            c_type_list.append(dict(odata.dtypes))
            top_ten_list.append(odata.iloc[:10].to_string())
        else:
            c_type_list.append("NA")
            top_ten_list.append("NA")

    df["Col_and_typ"] = c_type_list
    df["top_ten_cols"] = top_ten_list
    df = df.reset_index(drop=True)

    full_data = pd.read_json(
        "Lib/data_library.json",
    )

    full_data_ext = pd.concat([full_data, df], ignore_index=True).drop_duplicates(
        "Title"
    )
    full_data_ext = full_data_ext.loc[full_data_ext["top_ten_cols"] != "NA"]

    full_data_ext.to_json(
        "Lib/data_library.json", default_handler=str, orient="records", indent=4
    )
