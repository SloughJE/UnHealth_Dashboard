import dash
from dash import html, dcc, dash_table

from dash.dependencies import Input, Output
from dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import pandas as pd
import json

import plotly.graph_objects as go
from src.tabs.measure_view import (create_updated_map,find_top_bottom_values, value_to_color,
    df_measures, available_states, available_measures
)
from src.tabs.helper_data import CDC_PLACES_help, common_div_style, table_style,style_cell_conditional, style_header_conditional

info_icon = html.I(className="bi bi-info-circle", id="health-score-tooltip-target", style={'cursor': 'pointer', 'font-size': '22px', 'marginLeft': '10px'})
health_score_with_icon = html.H2(
    ["CDC PLACES Health Measures by County", info_icon],
    style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '28px',
        'margin': '0',
    }
)
health_tooltip = dbc.Tooltip(
    CDC_PLACES_help,
    target="health-score-tooltip-target",
    placement="right",
    className='custom-tooltip'
)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# Define the app layout with responsive design
app.layout = app.layout = dbc.Container([
    html.H1("Measure View", style={
        'color': 'white',
        'font-size':'5em',
        'textAlign': 'center',
        'margin-top': '20px',
    }), 

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
            }
        ),
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
            dash_table.DataTable(
                id='state-data-table',
                columns=[
                    {"name": "County", "id": "LocationName"},
                    {"name": "State", "id": "StateDesc"},
                    #{
                    #    "name": "Income per Capita", 
                    #    "id": "Per capita personal income",
                    #    "type": "numeric", 
                    #    "format": Format(group=Group.yes)  # Group by thousands
                    #},
                    {
                        "name": "Measure", 
                        "id": "Measure_short", 
                    },
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

# Define callback to update map and chart based on user input
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('measure-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_map_and_chart(selected_measure, selected_state):

    # Create and return the updated figures for map and bubble chart
    updated_map_fig = create_updated_map(df_measures, selected_state, selected_measure)

    return updated_map_fig

@app.callback(
    Output('state-data-table', 'data'),
    Output('state-data-table', 'style_data_conditional'),
    [Input('measure-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_table(selected_measure, selected_state):

    max_values = 10  # Number of top and bottom values
    df_measures_filtered = df_measures[(df_measures['Measure_short'] == selected_measure)]
    # Calculate the 10th and 90th percentiles of the data
    percentile_low = df_measures_filtered['Data_Value'].quantile(0.05)
    percentile_high = df_measures_filtered['Data_Value'].quantile(0.95)
    
    if selected_state:
        # Filter DataFrame based on selected state
        filtered_df = df_measures_filtered[df_measures_filtered['StateDesc'].isin(selected_state)]
    else:
        # If no state is selected, use the full dataset
        filtered_df = df_measures_filtered
    # Get top and bottom values based on filtered DataFrame

    top_bottom_df = find_top_bottom_values(filtered_df, 'Data_Value', max_values)
    # Calculate colors for each row in the top_bottom_df based on overall min and max values
    top_bottom_df['Color'] = top_bottom_df['Data_Value'].apply(lambda x: value_to_color(x, percentile_low, percentile_high))
    #top_bottom_df['Weighted_Score_Normalized'] = round(top_bottom_df.Weighted_Score_Normalized,2)

    #top_bottom_df['Per capita personal income'] = round(top_bottom_df['Per capita personal income'],0)
    #top_bottom_df.fillna("NA",inplace=True)

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