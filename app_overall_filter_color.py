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
    ["Health Score and Economic Data by County", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '28px',
        'margin': '0',
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

# Define the app layout with responsive design
app.layout = app.layout = dbc.Container([
    html.H1("Summary View", style={
        'color': 'white',
        'font-size':'5em',
        'textAlign': 'center',
        'margin-top': '20px',
    }), 

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
            }
        )
    ], style={
        'width': '30%',
        'margin': 'auto',
        'padding': '20px 0',
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
             html.H2("Ten Best and Worst County Health Scores", style={
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
                    {"name": "Health Score", "id": "Weighted_Score_Normalized"},
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

# Define callback to update map and chart based on user input
@app.callback(
    [Output('choropleth-map', 'figure'), Output('bubble-chart', 'figure')],
    [Input('state-dropdown', 'value')]
)
def update_map_and_chart(selected_state):

    # Create and return the updated figures for map and bubble chart
    updated_map_fig = create_updated_map(df_ranking, selected_state)
    updated_bubble_chart_fig = create_updated_bubble_chart(df_gam, selected_state,x_pred, y_pred, y_intervals,pseudo_r2_value)

    return updated_map_fig, updated_bubble_chart_fig

@app.callback(
    Output('state-data-table', 'data'),
    Output('state-data-table', 'style_data_conditional'),
    [Input('state-dropdown', 'value')]
)
def update_table(selected_state):
    max_values = 10  # Number of top and bottom values

    if selected_state:
        # Filter DataFrame based on selected state
        filtered_df = df_ranking[df_ranking['StateDesc'].isin(selected_state)]
    else:
        # If no state is selected, use the full dataset
        filtered_df = df_ranking
    # Get top and bottom values based on filtered DataFrame

    top_bottom_df = find_top_bottom_values(filtered_df, 'Weighted_Score_Normalized', max_values)
    # Calculate colors for each row in the top_bottom_df based on overall min and max values
    top_bottom_df['Color'] = top_bottom_df['Weighted_Score_Normalized'].apply(lambda x: value_to_color(x, percentile_low, percentile_high))
    top_bottom_df['Weighted_Score_Normalized'] = round(top_bottom_df.Weighted_Score_Normalized,2)

    top_bottom_df['Per capita personal income'] = round(top_bottom_df['Per capita personal income'],0)
    top_bottom_df.fillna("NA",inplace=True)

    # Convert DataFrame to dictionary for DataTable
    data = top_bottom_df.to_dict('records')

    # Define style conditions using the Color column
    style = [{'if': {'row_index': i}, 'backgroundColor': color} for i, color in enumerate(top_bottom_df['Color'])]

    # Additional style settings for borders and lines
    style.extend([
        {'if': {'column_id': 'LocationName'}, 'textAlign': 'left'},
        {'if': {'column_id': 'StateDesc'}, 'textAlign': 'left'}

    ])
    return data, style

if __name__ == '__main__':
    app.run_server(debug=True,port=8087)