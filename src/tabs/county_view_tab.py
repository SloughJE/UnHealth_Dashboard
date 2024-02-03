import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from src.tabs.county_view import (
                                create_county_econ_charts, create_county_health_charts, create_county_map, 
                                check_fips_county_data, create_kpi_layout,
                                df_all_counties, df_ranking_cv, df_bea, counties
                                )

from src.tabs.helper_data import common_div_style, centered_div_style, health_score_explanation


info_icon = html.I(className="bi bi-info-circle", id="health-score-tooltip-target", style={'cursor': 'pointer', 'font-size': '22px', 'marginLeft': '10px'})
county_health_score_with_icon = html.H2(
    ["UnHealth Score™ and Economic Data by County", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '32px',
        'margin': '20px',
    }
)
county_health_score_tooltip = dbc.Tooltip(
    health_score_explanation,
    target="health-score-tooltip-target",
    placement="right",
    className='custom-tooltip'
)

default_state = 'Alaska'  
default_county = 'Kusilvak'

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# App layout
# Define a function that returns the layout
def county_view_tab_layout():
    layout = dbc.Container([
        dcc.Interval(
        id='interval-component',
        interval=500,  # in milliseconds
        n_intervals=0,
        max_intervals=1  # Ensure it triggers only once
    ),
    county_health_score_with_icon,
    county_health_score_tooltip,
    html.Div([
        dbc.Col([
            dcc.Dropdown(
                id='county-view-state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df_ranking_cv['StateDesc'].unique())],
                value=default_state,  # Set default value
                placeholder="Select a State",
                style={'marginBottom': '10px', 'fontSize': '1.2em', 'width': '400px', 'margin': '10px auto', 'textAlign': 'left'}
            ),
            dcc.Dropdown(
                id='county-view-county-dropdown',
                value=default_county,  # Set default value
                placeholder="Select a County",
                style={'marginBottom': '10px', 'fontSize': '1.2em', 'width': '400px', 'margin': '0 auto', 'textAlign': 'left'}
            ),
            html.Div([
                html.Button(
                    'Show County Data', 
                    id='show-data-button', 
                    className='custom-button'
                )
            ], style={'display': 'flex', 'justifyContent': 'center'})  # Center-align the button
        ], width=12)
    ], style={
        'textAlign': 'center',  # This centers the container's content but won't affect dropdown text alignment.
        'margin': 'auto',
        'width': '50%',  # Adjust the width as per design requirements
        'border': 'none',
        'backgroundColor': 'transparent',
        }),

    html.Div(id='selected-title', style={'text-align': 'center', 'font-size': '3.5em', 'margin-bottom': '0px', 'margin': '0 auto'}),  
    
    dbc.Row([
        dbc.Col(html.Div(id='kpi-display', style={**common_div_style,'height': '95%'}), width=6),
        dbc.Col(html.Div(dcc.Graph(id='county-map'), style={**common_div_style, 'height': '95%'}), width=6)
    ], align="stretch"),  # Setting align to "stretch" for equal height columns
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(id='county-health-chart', style={'height': '800px'}),
                style=common_div_style
            ),
            width=12  # Use the full width of the row
        )
    ]),
    dbc.Row(
        dbc.Col([
            html.H4("Monetary Basis:", className='monetary-basis-heading'),
            dcc.RadioItems(
                id='currency-type',
                options=[
                    {'label': 'Adjusted Dollars (CPI)', 'value': 'adj'},
                    {'label': 'Current Dollars', 'value': 'current'}
                ],
                value='adj',  # Default value
                className='radio-button-style',
                inputStyle={"margin-right": "5px"},
                labelStyle={"display": "inline-block", "margin-right": "20px"},  # Make labels inline
                style={'text-align': 'center'}
            ),
            html.P("Select the basis for dollar values displayed in the charts below.", className='radio-button-instruction')
        ], width=12, className='text-center'),
        justify="center"
    ),
    dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(id='econ-chart-1'), style=common_div_style), 
                width=6
            ),
            dbc.Col(
                html.Div(dcc.Graph(id='econ-chart-2'), style=common_div_style), 
                width=6
            )
        ]),
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(id='econ-pop'), 
                style=common_div_style
            ),
            width=12  # Use the full width of the row
        )
    ]),
    ], fluid=True)

    return layout