from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import feedparser
from bs4 import BeautifulSoup
import io
import requests
from backend.data_manager import manager


def create_table(df: pd.DataFrame, highlights: list = None):
    """
    This function takes a DataFrame and turns it into a dash DataTable and converts it to a string in json-Format
        Input:
            df: DataFrame
        Output:
            list with Br-Component and DataTable
            str
            str
    """
    if highlights is None:

        # Display DataFrame in data-table-import tab
        data_table = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={"overflowX": "scroll"},
            style_cell={
                "minWidth": "180px",
                "width": "180px",
                "maxWidth": "180px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
        )

    else:
        style_data_conditional = [
            {
                "if": {"column_id": col},
                "backgroundColor": "rgba(0, 159, 227, 0.3)",  # Light blue background
                "color": "black",
            }
            for col in highlights
        ]
        data_table = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={"overflowX": "scroll"},
            style_cell={
                "minWidth": "180px",
                "width": "180px",
                "maxWidth": "180px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
            style_data_conditional=style_data_conditional,
        )

    # Display output of pandas.describe in data-structure-import tab
    manager.set_data(df)

    return [html.Br(), data_table]
    # return (
    #     [html.Br(), data_table],
    #     df.to_json(date_format="iso", orient="split"),
    # )


def return_error_popup(error_message: str):
    """
    This function serves to return a popup for a Dashboard and shall be used inside a callback for exceptions.
        Input:
            n_args: Number of arguments, the callback expects to return
            error_message: Error Message that should be displayed
        Output:
            dbc.Modal: A dashboard component that pops up
            None
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Warnung")),
            dbc.ModalBody(error_message),
        ],
        is_open=True,
    )


def extract_csv_link(soup: BeautifulSoup) -> str:
    """
    This function extracts the links to the csv files from the detail pages of the datasets on govdata
        Input:
            soup: BeautifulSoup source code from the detail pages
        Output:
            str: string with the link to the csv file
    """

    for a_tag in soup.find_all("a", href=True):
        if a_tag["href"].endswith("csv"):
            link = a_tag["href"]
            return link


def extract_keywords(soup: BeautifulSoup) -> list:
    """
    This function extracts the keywords from the detail pages of the datasets on govdata
        Input:
            soup: BeautifulSoup source code from the detail pages
        Output:
            list: list with the keywords as strings
    """
    try:
        dl_tag = soup.find("dl", class_="taglist space-bottom inline-list")

        # Extract all <dd> tags within the <dl> tag
        dd_tags = dl_tag.find_all("dd")

        # Extract the text from each <span> tag within the <dd> tags
        keywords = [dd.find("span").text for dd in dd_tags]
    except:
        keywords = []
    return keywords


def detect_sep(csv: str, num_lines=5) -> int:
    """
    This function is used to detect wether the csv files use comma or semicolon as separators
        Input:
            csv: csv file as string
            num_lines: number of lines used to determine the correct separator
        Output:
            str: either comma or semicolon
    """

    lines = csv.splitlines()[:num_lines]
    comma_count = sum(line.count(",") for line in lines)
    semicolon_count = sum(line.count(";") for line in lines)

    if comma_count > semicolon_count:
        return ","
    else:
        return ";"


def get_tags() -> list:
    """
    This function is used to return the different tags of the csv files as list
        Input:
            None
        Output:
            list: a list with the tags
    """

    full_data = pd.read_json(
        "Lib/data_library.json",
    )

    tag_list = list(full_data.Tag.unique())
    try:
        tag_list.remove("No Tag")
    except ValueError:
        pass
    return [{"label": item, "value": item} for item in tag_list]


def get_keywords() -> list:
    """
    This function is used to return the different keywords of the csv files as list
        Input:
            None
        Output:
            list: a list with the keywords
    """

    full_data = pd.read_json(
        "Lib/data_library.json",
    )

    all_values = [item for sublist in full_data["Keywords"] for item in sublist]
    return [{"label": item, "value": item} for item in list(set(all_values))]


def get_govdata_dataset(link: str) -> pd.DataFrame:
    """
    This function retrieves a dataset from govdata by link
        Input:
            link: a link to the csv file
        Output:
            pd.Dataframe: govdata dataframe
    """
    response = requests.get(link)

    csv_content = response.content.decode("iso-8859-1")

    return pd.read_csv(io.StringIO(csv_content), sep=detect_sep(csv_content))
