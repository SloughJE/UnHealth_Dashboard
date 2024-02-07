import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.tabs.county_view import df_ranking_cv
from src.tabs.helper_data import common_div_style, unhealth_score_explanation


info_icon = html.I(className="bi bi-info-circle", id="unhealth-score-county-tooltip-target", 
                   style={
                       'cursor': 'pointer', 
                        'font-size': '22px', 
                        'marginLeft': '10px',
                        })
county_unhealth_score_with_icon = html.H2(
    ["UnHealth Score™ and Economic Data by County", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '32px',
        'margin': '20px',
    }
)
county_unhealth_score_tooltip = dbc.Tooltip(
    unhealth_score_explanation,
    target="unhealth-score-county-tooltip-target",
    placement="right",
    className='custom-tooltip',    
    style={'white-space': 'pre-line'}
)

default_state = 'Alaska'  
default_county = 'Kusilvak'

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# App layout
def county_view_tab_layout():
    layout = dbc.Container([
        dcc.Interval(
        id='interval-component',
        interval=500,  # in milliseconds
        n_intervals=0,
        max_intervals=1  # Ensure it triggers only once
    ),
    county_unhealth_score_with_icon,
    county_unhealth_score_tooltip,
    html.Div([
        dbc.Col([
            dcc.Dropdown(
                id='county-view-state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df_ranking_cv['StateDesc'].unique())],
                value=default_state,  
                placeholder="Select a State",
                style={'marginBottom': '10px', 'fontSize': '1.2em', 'width': '400px', 'margin': '10px auto', 'textAlign': 'left',
                                       'backgroundColor': '#303030'}
            ),
            dcc.Dropdown(
                id='county-view-county-dropdown',
                value=default_county,  
                placeholder="Select a County",
                style={'marginBottom': '10px', 'fontSize': '1.2em', 'width': '400px', 'margin': '0 auto', 'textAlign': 'left',
                       'backgroundColor': '#303030'}
            ),
            html.Div([
                html.Button(
                    'Show County Data', 
                    id='show-data-button', 
                    className='custom-button'
                )
            ], style={'display': 'flex', 'justifyContent': 'center'})  
        ], width=12)
        ], style={
            'textAlign': 'center',  
            'margin': 'auto',
            'width': '50%',  
            'border': 'none',
            'backgroundColor': 'transparent',
        }),

    html.Div(id='selected-title', style={'text-align': 'center', 'font-size': '3.5em', 'margin-bottom': '0px', 'margin': '0 auto'}),  
    
    dbc.Row([
        dbc.Col(html.Div(id='kpi-display', style={**common_div_style,'height': '95%'}), width=6),
        dbc.Col(html.Div(dcc.Graph(id='county-map'), style={**common_div_style, 'height': '95%'}), width=6)
    ], align="stretch"),  
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(id='county-health-chart', style={'height': '800px'}),
                style=common_div_style
            ),
            width=12  
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
                value='adj',  
                className='radio-button-style',
                inputStyle={"margin-right": "5px"},
                labelStyle={"display": "inline-block", "margin-right": "20px"},  
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
            width=12  
        )
    ]),
    ], fluid=True)

    return layout