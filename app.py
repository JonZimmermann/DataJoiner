from dash import Dash, html, Input, Output, callback, State, dcc
from flask import g
import dash
import dash_bootstrap_components as dbc
import schedule
import time
from backend.library_update import library_update

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    use_pages=True,
    suppress_callback_exceptions=True,
)  # unter external Stylesheet kann ein eigenes css-File hinterlegt werden
server = app.server

# A Container component. Containers provide a means to center and horizontally pad the site’s contents.
app.layout = dbc.Container(
    [  # Overhead Navigation Bar with the Deloitte Logo, a Title and a Button to unfold the Offacnvas
        dbc.Navbar(
            [
                dbc.NavbarBrand(
                    [
                        html.Img(
                            src=dash.get_asset_url("logo.png"),
                            height="40px",
                            style={
                                "borderRadius": "50%",
                                "marginRight": "20px",
                                "marginLeft": "10px",
                            },
                        ),
                        "Data Integration Platform",
                    ],
                    href="/",
                    className="mr-4",
                    style={"color": "white"},
                ),
            ],
            color="#0077ae",
        ),
        # This component will store the DataFrame used in this session in it's data attribute for the duration of the session, data kept on client side with id as key
        dcc.Store(id="data-store", storage_type="memory"),
        dash.page_container,
    ]
)

###############################################################################################
# CALLBACKS
###############################################################################################


###############################################################################################
# LIBRARY UPDATE
schedule.every().day.at("10:30").do(library_update)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


###############################################################################################

if __name__ == "__main__":
    app.run_server(debug=True)
    run_scheduler()
