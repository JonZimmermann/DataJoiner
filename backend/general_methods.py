from dash import html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from bs4 import BeautifulSoup
import io
import requests
from backend.data_manager import manager


def create_table(df: pd.DataFrame, highlights: list = None) -> list:
    """
    Converts a DataFrame into a Dash DataTable and returns it along with a line break component.

    If highlights are provided, specific columns will be highlighted.

    Parameters:
    ----------
    df : pd.DataFrame
        The DataFrame to be displayed in the Dash DataTable.
    highlights : list, optional
        A list of column names to be highlighted in the DataTable (default is None).

    Returns:
    -------
    list
        A list containing a Dash HTML component (line break) and the Dash DataTable.
    """

    if highlights is None:

        ## Display DataFrame in a Data Table without highlights
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
        # Highlight the new columns in the Data Table
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

    # Store DataFrame in Data Manager
    manager.set_data(df)

    return [html.Br(), data_table]


def return_error_popup(error_message: str) -> dbc.Modal:
    """
    Returns a Dash Bootstrap Components Modal to display an error message.

    Parameters:
    ----------
    error_message : str
        The error message to be displayed in the popup.

    Returns:
    -------
    dbc.Modal
        A dbc Modal with the error message.
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
    Extracts the link to the CSV file from the detail pages of the datasets on govdata.

    Parameters:
    ----------
    soup : BeautifulSoup
        The BeautifulSoup object containing the parsed HTML of the detail page.

    Returns:
    -------
    str
        The link to the CSV file.
    """

    for a_tag in soup.find_all("a", href=True):
        if a_tag["href"].endswith("csv"):
            link = a_tag["href"]
            return link


def extract_keywords(soup: BeautifulSoup) -> list:
    """
    Extracts the keywords from the detail pages of the datasets on govdata.

    Parameters:
    ----------
    soup : BeautifulSoup
        The BeautifulSoup object containing the parsed HTML of the detail page.

    Returns:
    -------
    list
        A list of keywords extracted from the detail page.
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
    Detects whether the CSV file uses a comma or semicolon as the separator.

    Parameters:
    ----------
    csv : str
        The CSV file content as a string.
    num_lines : int, optional
        The number of lines used to determine the correct separator (default is 5).

    Returns:
    -------
    str
        The detected separator, either a comma or semicolon.
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
    Returns the different tags of the CSV files on govdata as a list.

    Returns:
    -------
    list
        A list of tags, each represented as a dictionary with 'label' and 'value'.
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
    Returns the different keywords of the CSV files on govdata as a list.

    Returns:
    -------
    list
        A list of keywords, each represented as a dictionary with 'label' and 'value'.
    """

    full_data = pd.read_json(
        "Lib/data_library.json",
    )

    all_values = [item for sublist in full_data["Keywords"] for item in sublist]
    return [{"label": item, "value": item} for item in list(set(all_values))]


def get_govdata_dataset(link: str) -> pd.DataFrame:
    """
    Retrieves a dataset from govdata by the given link.

    Parameters:
    ----------
    link : str
        The link to the CSV file.

    Returns:
    -------
    pd.DataFrame
        The retrieved dataset as a Pandas DataFrame.
    """
    response = requests.get(link)

    csv_content = response.content.decode("iso-8859-1")

    return pd.read_csv(io.StringIO(csv_content), sep=detect_sep(csv_content))
