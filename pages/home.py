import dash
from dash import html, callback, Input, Output, State, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import plotly.figure_factory as ff
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
            [  # Accordion component, Filled with Items, could be extended with further Items if necessary
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                html.Div(
                                    [  # Tabs component, Filled with Tab-Component, could be replaced in later iterations or extended with further Items if necessary
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    [
                                                        html.Br(),
                                                        html.H3("Import aus csv-Datei"),
                                                        html.P(
                                                            "Laden Sie hier eine xlsx-Datei oder eine csv-Datei hoch. Die csv-Datei sollte den folgenden Anforderungen genügen:"
                                                        ),
                                                        html.Ol(
                                                            [
                                                                html.Li(
                                                                    "Trennzeichen:   ';'"
                                                                ),
                                                                html.Li(
                                                                    "Dezimaltrennzeichen:   '.'"
                                                                ),
                                                            ]
                                                        ),
                                                        dcc.Upload(
                                                            id="upload",
                                                            children=html.Div(
                                                                [
                                                                    "Ziehen sie oder ",
                                                                    html.A(
                                                                        "klicken sie um eine Datei auszuwählen"
                                                                    ),
                                                                ]
                                                            ),
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
                                                    label="Import aus csv oder xlsx-Datei",
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
                        dbc.AccordionItem(
                            [
                                # all tags as Dropdown#
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dcc.Dropdown(
                                                                options=gm.get_tags(),
                                                                clearable=True,
                                                                searchable=True,
                                                                placeholder="Thema ihres Datensatzes",
                                                                id="tags-dropdown",
                                                            ),
                                                        ]
                                                    )
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            html.Center(
                                                                [
                                                                    dbc.Button(
                                                                        "Datensätze suchen",
                                                                        color="primary",
                                                                        id="search-button",
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        dcc.Dropdown(
                                                            options=gm.get_keywords(),
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
                        dbc.AccordionItem(
                            [
                                html.Div(
                                    [
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    [
                                                        html.Div(
                                                            [
                                                                dbc.Button(
                                                                    "Download CSV",
                                                                    id="download-button",
                                                                    color="primary",
                                                                    className="mt-3",
                                                                    active=False,
                                                                ),
                                                                dcc.Download(
                                                                    id="download-dataframe"
                                                                ),
                                                            ]
                                                        ),
                                                        html.Div(
                                                            id="data-table-import"
                                                        ),
                                                    ],
                                                    label="Datentabelle",
                                                    id="data-table-tab",
                                                ),
                                            ]
                                        )
                                    ]
                                )
                            ],
                            title="Daten",
                            item_id="data",
                        ),
                    ],
                    active_item="upload",
                    always_open=True,
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
    Output("data-table-import", "children"),
    Input("upload", "contents"),
    State("upload", "filename"),
)
def process_uploaded_file(contents, filename):
    """
    This Callback takes the uploaded file as Base64 String which should be a csv or xlsx and converts it to a pd.DataFrame.
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
                    decimal=".",
                    parse_dates=True,
                )

            except:
                return gm.return_error_popup(
                    3,
                    "Datei konnte nicht gelesen werden, bitte prüfen Sie die Anforderungen an csv-Dateien, überprüfen Sie auch die Datumsformate",
                )

        else:
            return gm.return_error_popup(
                3,
                "Ungültiges Dateiformat. Bitte verwenden Sie eine CSV-Datei",
            )

        return gm.create_table(df)

    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("data-table-import", "children"),
    Output("download-button", "active"),
    Input("search-button", "n_clicks"),
    State("tags-dropdown", "value"),
    State("keys-dropdown", "value"),
)
def joiner(_, data, tag, keys):
    catalog = pd.read_json(
        "Lib/data_library.json",
    )

    catalog = catalog[
        (catalog["Keywords"].apply(lambda x: any(elem in x for elem in keys)))
        & (catalog.Tag == tag)
    ]

    user_dataset = manager.get_data()

    # solution = mistral_retriever(catalog, user_dataset)
    solution = {
        "dataset_id": 0,
        "col_name_user": "Tatort",
        "col_name_catalog": "Tatort",
    }

    if solution is None:
        # return an error message via popup
        pass

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

        except KeyError:
            # error popup
            pass

        # wrap dataset inside plotly component
        return gm.create_table(combined_df, highlights=added_columns), True


@callback(
    Output("download-dataframe", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True,
)
def download(_):
    return dcc.send_data_frame(manager.get_data(), "data_table.csv")
