import dash
from dash import html, dcc, dash_table

from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc

from src.tabs.measure_view import available_states, available_measures
from src.tabs.helper_data import CDC_PLACES_help, common_div_style, table_style,style_cell_conditional, style_header_conditional

info_icon = html.I(className="bi bi-info-circle", id="cdc-places-tooltip-target", style={'cursor': 'pointer', 'font-size': '22px', 'marginLeft': '10px'})
health_score_with_icon = html.H2(
    ["CDC PLACES Health Measures", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '32px',
        'margin': '20px',
    }
)
health_tooltip = dbc.Tooltip(
    CDC_PLACES_help,
    target="cdc-places-tooltip-target",
    placement="right",
    className='custom-tooltip'
)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# Define the app layout with responsive design
def measure_view_tab_layout():
    layout = dbc.Container([

    health_score_with_icon,
    health_tooltip,
    html.Div([
            dcc.Dropdown(
            id='measure-dropdown',
            options=[{'label': measure, 'value': measure} for measure in available_measures],
            multi=False,
            placeholder='Select a Measure',
            value=available_measures[0],
            clearable=False,  # Prevent users from clearing the selection
            style={
                'color': 'white',  # Text color
                'backgroundColor': '#303030',  # Dropdown background color
                'borderRadius': '5px',  # Rounded corners
                'fontSize': '20px',
                'margin-bottom': '10px'

            }
        ),
        dcc.Dropdown(
            id='measure-view-state-dropdown',
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
        #'padding': '20px 20px',
        'border': 'none',  # Remove any border from the parent div
        'backgroundColor': 'transparent',  # Ensure background is transparent
    }),

    dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(id='measure-view-choropleth-map', figure={}), style=common_div_style),
                width=12
            ),
        ]),
    
    dbc.Row([
        dbc.Col(
        html.Div([
             html.H2("Ten Best and Worst Scores", style={
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
            html.H4("", id='measure-subtitle', style={
                'color': 'white',
                'textAlign': 'center',
                'fontSize': '26px',
                'marginTop': '0px',
                'marginBottom': '10px',
            }),
            dash_table.DataTable(
                id='measure-view-state-data-table',
                columns=[
                    {"name": "County", "id": "LocationName"},
                    {"name": "State", "id": "StateDesc"},
                    {"name": "Percent", "id": "Data_Value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.percentage)},
                    {"name": "Measure Rank", "id": "County Measure Rank"},
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
    