import dash
from dash import html, callback, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import backend.general_methods as gm
from backend.data_manager import manager
from backend.llm import mistral_retriever


#####################################################################################################
#####################################################################################################
# registers the page with app.py
dash.register_page(__name__, path="/")
# A Container component. Containers provide a means to center and horizontally pad the site’s contents.
layout = dbc.Container(
    [
        html.Div(
            [  # Accordion component: allows multiple sections to expand and collapse
                dbc.Accordion(
                    [
                        # First Accordion Item: Upload File section
                        dbc.AccordionItem(
                            [
                                html.Div(
                                    [
                                        # Tabs component: allows for tabbed navigation within the Upload File section
                                        # could be replaced in later iterations or extended with further Items if necessary
                                        dcc.Tabs(
                                            [
                                                # First Tab: Import from CSV file
                                                dcc.Tab(
                                                    [
                                                        html.Br(),
                                                        # HEader
                                                        html.H3("Import aus csv-Datei"),
                                                        # Instruction
                                                        html.P(
                                                            "Laden Sie hier eine csv-Datei hoch. Die csv-Datei sollte den folgenden Anforderungen genügen:"
                                                        ),
                                                        # Ordered list specifying file requirements
                                                        html.Ol(
                                                            [
                                                                html.Li(
                                                                    "Trennzeichen:   ';'"
                                                                ),
                                                                html.Li(
                                                                    "Dezimaltrennzeichen:   ','"
                                                                ),
                                                            ]
                                                        ),
                                                        # Upload component for CSV files
                                                        dcc.Upload(
                                                            id="dataframe-upload",
                                                            children=html.Div(
                                                                [
                                                                    "Ziehen sie oder ",
                                                                    html.A(
                                                                        "klicken sie um eine Datei auszuwählen"
                                                                    ),
                                                                ]
                                                            ),
                                                            # Styling for the upload box
                                                            style={
                                                                "width": "50%",
                                                                "height": "60px",
                                                                "lineHeight": "60px",
                                                                "borderWidth": "1px",
                                                                "borderStyle": "dashed",
                                                                "borderRadius": "5px",
                                                                "textAlign": "center",
                                                                "margin": "10px",
                                                            },
                                                        ),
                                                    ],
                                                    label="Import aus csv-Datei",
                                                ),
                                            ]
                                        )
                                    ],
                                    style={"padding": "15px"},
                                ),
                            ],
                            title="Upload File",
                            item_id="upload",
                        ),
                        # Second Accordion Item: Selection of Topics and Keywords section
                        dbc.AccordionItem(
                            [
                                # all tags as Dropdown#
                                html.Div(
                                    [
                                        # Row and column structure for the different dropdown menus
                                        dbc.Row(
                                            [
                                                # Column for tags dropdown
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dcc.Dropdown(
                                                                options=gm.get_tags(),  # Options to choose tags from
                                                                clearable=True,
                                                                searchable=True,
                                                                placeholder="Thema ihres Datensatzes",
                                                                id="tags-dropdown",
                                                            ),
                                                        ]
                                                    )
                                                ),
                                                # Column for the search button
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            html.Center(
                                                                [
                                                                    dbc.Button(
                                                                        "Datensätze suchen",
                                                                        id="search-button",
                                                                        style={
                                                                            "background-color": "#00305D"
                                                                        },
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ),
                                                # Column for keywords dropdown
                                                dbc.Col(
                                                    html.Div(
                                                        dcc.Dropdown(
                                                            options=gm.get_keywords(),  # Options to choose keys from
                                                            clearable=True,
                                                            searchable=True,
                                                            placeholder="Schlüsselwörter zu ihrem Datensatzes",
                                                            multi=True,
                                                            id="keys-dropdown",
                                                        ),
                                                    )
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            title="Auswahl von Themen und Schlüsselwörtern",
                            item_id="topics_keys",
                        ),
                        # Third Accordion Item: Data section
                        dbc.AccordionItem(
                            [
                                # Tabs not strictly necessary. Design choice as it looked well + easily extendable with more data info
                                dcc.Tabs(
                                    [
                                        dcc.Tab(
                                            [
                                                html.Div(
                                                    [
                                                        # Button to download the data as CSV, initially disabled, enabled after data matching
                                                        dbc.Button(
                                                            "CSV herunterladen",
                                                            id="download-button",
                                                            className="mt-3",
                                                            disabled=True,
                                                            style={
                                                                "background-color": "#00305D"
                                                            },
                                                        ),
                                                        # Component for downloading data
                                                        dcc.Download(
                                                            id="download-dataframe"
                                                        ),
                                                    ]
                                                ),
                                                # Placeholder for the data table
                                                html.Div(id="data-table-import"),
                                            ],
                                            label="Datentabelle",
                                            id="data-table-tab",
                                        ),
                                    ]
                                )
                            ],
                            title="Daten",
                            item_id="data",
                        ),
                    ],
                    active_item="upload",  # Initially open accordion item
                    always_open=True,  # All items can be open at the same time
                    id="accordion",
                )
            ],
            style={"padding": "30px"},
        )
    ]
)

###############################################################################################
# CALLBACKS
###############################################################################################


@callback(
    Output("data-table-import", "children", allow_duplicate=True),
    Output("accordion", "active_item", allow_duplicate=True),
    Input("dataframe-upload", "contents"),
    State("dataframe-upload", "filename"),
    prevent_initial_call=True,
)
def process_uploaded_file(contents, filename):
    """
    This Callback takes the uploaded file as Base64 String which should be a csv and converts it to a pd.DataFrame.
    The Dataframe is then passed to table_and_structure(), which processes it and generates a dash DataTable, a string with the output of df.describe() and
    a json String to be stored in the Store component in app.py
        Input:
            contents: str Base64
            filename: str Filename
        Output:
            data-table-import: Dash DataTable Component
            data-structure-import: str
            data-store: str json formatted str for Store component
    """
    if contents is not None:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(
                    io.StringIO(decoded.decode("iso-8859-1")),
                    delimiter=";",
                    decimal=",",
                    parse_dates=True,
                )

            except:
                return [
                    gm.return_error_popup(
                        "Datei konnte nicht gelesen werden, bitte prüfen Sie die Anforderungen an csv-Dateien, überprüfen Sie auch die Datumsformate",
                    ),
                    "upload",
                ]

        else:
            return [
                gm.return_error_popup(
                    "Ungültiges Dateiformat. Bitte verwenden Sie eine CSV-Datei",
                ),
                "upload",
            ]

        return gm.create_table(df), "topics_keys"

    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("data-table-import", "children"),
    Output("download-button", "disabled"),
    Output("accordion", "active_item"),
    Input("search-button", "n_clicks"),
    State("tags-dropdown", "value"),
    State("keys-dropdown", "value"),
    prevent_initial_call=True,
)
def joiner(_, tag, keys):
    """
    Filter the data catalog based on user-selected tags and keywords,
    and attempt to join the user-provided dataset with a matching dataset from the catalog.
    The match is provided through the use of a Large Language Model

    Parameters:
        _: Placeholder for the unused parameter n_clicks
        tag: The selected tag to filter datasets in the catalog.
        keys: The selected keywords to filter datasets in the catalog.

    Returns:
        tuple: A tuple containing:
            - A Dash component (DataTable or error popup).
            - A boolean indicating whether downloading the dataframe is enabled or not (only enabled if dataframe is updated)

    Function logic:
    1. Load the data catalog from the JSON file it is stored in.
    2. Filter the catalog based on the provided tag and/or keywords.
    3. Retrieve the user's dataset from the DataManager instance.
    4. Use a Large Language Model to find the best matching dataset from the catalog.
    5. Attempt to join the user dataset with the candidate dataset from the catalog.
    6. If successful, create and return a DataTable with the combined dataset and allow downloading the dataset
    7. If unsuccessful, return an error popup message.

    Notes:
        - The machine learning model part is commented out for demonstration. It must be uncommented if enough resources are available
        - Proper error handling ensures that any issues during the join process result in an informative error popup.
    """

    catalog = pd.read_json("Lib/data_library.json", encoding="iso-8859-1")
    if tag is None and keys is None:
        pass

    elif tag is None:
        catalog = catalog[
            (catalog["Keywords"].apply(lambda x: any(elem in x for elem in keys)))
        ]

    elif keys is None:
        catalog = catalog[(catalog.Tag == tag)]

    else:
        catalog = catalog[
            (catalog["Keywords"].apply(lambda x: any(elem in x for elem in keys)))
            & (catalog.Tag == tag)
        ]

    user_dataset = manager.get_data()

    solution = {
        "dataset_id": 4,
        "col_name_user": "Tatb-Nr.",
        "col_name_catalog": "Tatb-Nr.",
    }

    # if this line is enabled, the model uses the LLM, used in production, disabled for demo
    # solution = mistral_retriever(catalog, user_dataset) # if this line is enabled, the model uses the LLM, used for

    if solution is None:
        # return an error message via popup
        return [
            gm.return_error_popup(
                "Leider konnte kein passender Datensatz gefunden werden."
            ),
            True,
            "topics_keys",
        ]

    else:
        candidate_link = catalog.loc[solution["dataset_id"], "CSV"]

        # get full dataset
        candidate_df = gm.get_govdata_dataset(candidate_link)

        # join dataset
        try:
            combined_df = pd.merge(
                user_dataset,
                candidate_df,
                left_on=solution["col_name_user"],
                right_on=solution["col_name_catalog"],
                how="left",
            )

            added_columns = list(combined_df.columns[len(user_dataset.columns) :])

        except:
            # error popup
            return [
                gm.return_error_popup(
                    f"Leider gab es ein Problem beim Integrationsprozess. Bitte zeigen Sie den Fehler den Entwicklern an und versuchen Sie es später noch einmal. Catalog Reference: {solution['dataset_id']}"
                ),
                True,
                "topics_keys",
            ]

        # wrap dataset inside plotly component, allow download
        return gm.create_table(combined_df, highlights=added_columns), False, "data"


@callback(
    Output("download-dataframe", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True,
)
def download(_):
    """Downloads the updated csv file"""
    return dcc.send_data_frame(manager.get_data().to_csv, "data_table.csv")
