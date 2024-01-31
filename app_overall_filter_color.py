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
    df_ranking, df_gam, x_pred, y_pred, y_intervals, available_states,percentile_low, percentile_high
)
# Style for the data table
table_style = {
    'style_table': {
        'overflowX': 'auto',
        'width': '50%',
        'margin': 'auto',
        'border': '1px solid white'
    },
    'style_cell': {
        #'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'black',
        'border': '1px solid grey',
        'textAlign': 'center',
        'padding': '5px',
        'fontWeight': 'bold',

    },
    'style_header': {
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'border': '1px solid grey',
        'fontWeight': 'bold',
        'textAlign': 'center'
    }
}

style_header_conditional=[
    {
        'if': {'column_id': 'Weighted_Score_Normalized'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'Rank'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'LocationName'},
        'textAlign': 'center'
    },
    {
        'if': {'column_id': 'StateDesc'},
        'textAlign': 'center'
    },
    {
        'if': {'column_id': 'Population'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'Real GDP Per Capita'},
        'textAlign': 'right'
    }
]


style_cell_conditional=[
    {
        'if': {'column_id': 'Weighted_Score_Normalized'},
        'width': '15%',  
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'Rank'},
        'width': '10%',  
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'LocationName'},
        'textAlign': 'left'
    },
    {
        'if': {'column_id': 'StateDesc'},
        'textAlign': 'left'
    },
        {
        'if': {'column_id': 'Population'},
        'textAlign': 'right',
        'width': '15%',  

    },
    {
        'if': {'column_id': 'Real GDP Per Capita'},
        'textAlign': 'right',
        'width': '15%',  

    }
]


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# Define the app layout with responsive design
app.layout = html.Div([
    html.H1("Overall Health Score and GDP per Capita by County for 2020", style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '42px',
        'margin': '0',
        'padding': '20px 0'
    }),

    html.Div([
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in available_states],
            multi=True,
            placeholder='Select a State or States',
            style={
                'color': '#212121',  # Text color
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

    # Map and Bubble Chart with adjusted padding
    html.Div([
        html.Div([
            dcc.Graph(id='choropleth-map', figure={})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '0', 'height': '80vh', 'marginBottom': '0'}),
        html.Div([
            dcc.Graph(id='bubble-chart', figure={})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '0', 'height': '80vh', 'marginBottom': '0'})
    ], style={'display': 'flex', 'backgroundColor': 'black', 'flexWrap': 'wrap','padding':'0', 'marginBottom': '0'}), 

    # Title for Table
    html.Div(
        html.H2("Ten Worst and Best County Health Scores", style={
            'color': 'white',
            'textAlign': 'center',
            'fontSize': '30px',
            'marginTop': '0',
            'marginBottom': '0',
            'textDecoration': 'none',
            'borderBottom': 'none',
            'backgroundColor': 'black',
            'padding': '0'
        }),
        style={
            'backgroundColor': 'black',
            'border': 'none',
            'margin': '0',
            'padding': '0'
        }
    ),

    # Data Table
    html.Div([
        dash_table.DataTable(
            id='state-data-table',
            columns=[
                {"name": "County", "id": "LocationName"},
                {"name": "State", "id": "StateDesc"},
                {
                    "name": "GDP per Capita", 
                    "id": "Real GDP Per Capita",
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
    ], style={'textAlign': 'center', 'backgroundColor': 'black', 'padding': '20px', 'border': 'none'})

], style={
    'backgroundColor': 'black',
    'margin': '0',
    'padding': '0',
    'height': '100vh',
    'border': 'none'
})

# Define callback to update map and chart based on user input
@app.callback(
    [Output('choropleth-map', 'figure'), Output('bubble-chart', 'figure')],
    [Input('state-dropdown', 'value')]
)
def update_map_and_chart(selected_state):
    # Filter your data based on selected_state and 
    # Update the map and bubble chart based on the filtered data

    # Create and return the updated figures for map and bubble chart
    updated_map_fig = create_updated_map(df_ranking, selected_state)
    updated_bubble_chart_fig = create_updated_bubble_chart(df_gam, selected_state,x_pred, y_pred, y_intervals)

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
        filtered_df = df_ranking[df_ranking['StateAbbr'].isin(selected_state)]
    else:
        # If no state is selected, use the full dataset
        filtered_df = df_ranking
    # Get top and bottom values based on filtered DataFrame

    top_bottom_df = find_top_bottom_values(filtered_df, 'Weighted_Score_Normalized', max_values)
    # Calculate colors for each row in the top_bottom_df based on overall min and max values
    top_bottom_df['Color'] = top_bottom_df['Weighted_Score_Normalized'].apply(lambda x: value_to_color(x, percentile_low, percentile_high))
    top_bottom_df['Weighted_Score_Normalized'] = round(top_bottom_df.Weighted_Score_Normalized,2)

    top_bottom_df['Real GDP Per Capita'] = round(top_bottom_df['Real GDP Per Capita'],0)
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
    app.run_server(debug=True)