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
    [  # Overhead Navigation Bar with the Logo and a Title
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
        # imports the page structure
        dash.page_container,
    ]
)

###############################################################################################
# CALLBACKS
###############################################################################################
# for multiple callbacks referring to the same entity etx. all Callbacks can be migrated to this section

###############################################################################################
# LIBRARY UPDATE
###############################################################################################

schedule.every().day.at("10:30").do(library_update)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


###############################################################################################

if __name__ == "__main__":
    app.run_server(debug=True)
    run_scheduler()
