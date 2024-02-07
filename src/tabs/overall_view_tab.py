import dash
from dash import html, dcc, dash_table
from dash.dash_table.Format import Format, Group
import dash_bootstrap_components as dbc

from src.tabs.overall_view import available_states
from src.tabs.helper_data import unhealth_score_explanation, common_div_style, table_style,style_cell_conditional, style_header_conditional


info_icon = html.I(className="bi bi-info-circle", id="unhealth-score-tooltip-target", style={'cursor': 'pointer','textAlign':'left', 'font-size': '22px', 'marginLeft': '10px'})
unhealth_score_with_icon = html.H2(
    ["UnHealth Score™ and Economic Data Summary", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '32px',
        'margin': '20px',
    }
)
unhealth_score_tooltip = dbc.Tooltip(
    unhealth_score_explanation,
    target="unhealth-score-tooltip-target",
    placement="right",
    className='custom-tooltip',
    style={'white-space': 'pre-line'}
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])


def overall_view_tab_layout():
    layout = dbc.Container([

    unhealth_score_with_icon,
    unhealth_score_tooltip,
    html.Div([
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in available_states],
            multi=True,
            placeholder='Select a State or States',
            style={

                'backgroundColor': '#303030',  
                'borderRadius': '5px', 
                'fontSize': '20px',
                'margin-bottom': '20px'
            }
        )
    ], style={
        'width': '30%',
        'margin': 'auto',
        'border': 'none',  
        'backgroundColor': 'transparent', 
    }),

    dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(id='choropleth-map', figure={}), style=common_div_style),
                width=6
            ),
            dbc.Col(
                    html.Div(dcc.Graph(id='scatter-chart', figure={}), style=common_div_style),
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
                        "format": Format(group=Group.yes)  
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
            width=12  
        )
    ]),

    ],fluid=True)

    return layout