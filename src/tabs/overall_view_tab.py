import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format, Group
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import pandas as pd
import json

import plotly.graph_objects as go
from src.tabs.overall_view import (create_updated_bubble_chart,create_updated_map,find_top_bottom_values, value_to_color,
    df_ranking, df_gam, x_pred, y_pred, y_intervals, available_states,percentile_low, percentile_high, pseudo_r2_value
)
from src.tabs.helper_data import health_score_explanation, common_div_style, table_style,style_cell_conditional, style_header_conditional


info_icon = html.I(className="bi bi-info-circle", id="health-score-tooltip-target", style={'cursor': 'pointer', 'font-size': '22px', 'marginLeft': '10px'})
health_score_with_icon = html.H2(
    ["UnHealth Score™ and Economic Data Summary", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '32px',
        'margin': '20px',
    }
)
health_score_tooltip = dbc.Tooltip(
    health_score_explanation,
    target="health-score-tooltip-target",
    placement="right",
    className='custom-tooltip'
)
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# Define a function that returns the layout
def overall_view_tab_layout():
    layout = dbc.Container([

    health_score_with_icon,
    health_score_tooltip,
    html.Div([
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in available_states],
            multi=True,
            placeholder='Select a State or States',
            style={
                'color': 'white',  # Text color
                'backgroundColor': '#303030',  # Dropdown background color
                'borderRadius': '5px',  # Rounded corners
                'fontSize': '20px',
                'margin-bottom': '20px'
            }
        )
    ], style={
        'width': '30%',
        'margin': 'auto',
        #'padding': '20px 0',
        'border': 'none',  # Remove any border from the parent div
        'backgroundColor': 'transparent',  # Ensure background is transparent
    }),

    dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(id='choropleth-map', figure={}), style=common_div_style),
                width=6
            ),
            dbc.Col(
                    html.Div(dcc.Graph(id='bubble-chart', figure={}), style=common_div_style),
                width=6
            )
        ]),
    
    dbc.Row([
        dbc.Col(
        html.Div([
             html.H2("Ten Best and Worst UnHealth Scores", style={
            'color': 'white',
            'textAlign': 'center',
            'fontSize': '30px',
            'marginTop': '0px',
            'marginBottom': '0',
            'textDecoration': 'none',
            'borderBottom': 'none',
            'backgroundColor': 'black',
            'padding': '0'
        }),
            dash_table.DataTable(
                id='state-data-table',
                columns=[
                    {"name": "County", "id": "LocationName"},
                    {"name": "State", "id": "StateDesc"},
                    {
                        "name": "Income per Capita", 
                        "id": "Per capita personal income",
                        "type": "numeric", 
                        "format": Format(group=Group.yes)  # Group by thousands
                    },
                    {
                        "name": "Population", 
                        "id": "Population",
                        "type": "numeric", 
                        "format": Format(group=Group.yes)  # Group by thousands
                    },
                    {"name": "UnHealth Score", "id": "Weighted_Score_Normalized"},
                    {"name": "Overall Rank", "id": "Rank"},
                ],
                data=[],
                style_cell_conditional=style_cell_conditional,
                style_header_conditional=style_header_conditional,
                **table_style
            )
        ], style=common_div_style),
            width=12  # Use the full width of the row
        )
    ]),

    ],fluid=True)

    return layout