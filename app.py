import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

filepath_health_data = "data/interim/health_food_2020.pickle"
df = pd.read_pickle(filepath_health_data)  
df['Data_Value'] = df['Data_Value'] / 100

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)

max_values = 10

def value_to_color(value, min_val, max_val, colormap=plt.cm.RdYlGn_r):
    """Convert a value to a color using a matplotlib colormap."""
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
    return mcolors.to_hex(colormap(norm(value)))

table_style_cell = {
    'fontFamily': 'Arial, sans-serif',  # Use a readable font
    'fontSize': 18,  # Increase font size
    'textAlign': 'left',
}

table_style_header = {
    'fontWeight': 'bold',
    'fontSize': 22,
    'backgroundColor': '#f4f4f4',  # Light gray background in headers
    'color': 'black'
}

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Dropdown(
        id='measure-dropdown',
        options=[{'label': i, 'value': i} for i in df['Measure'].unique()],
        value='Diagnosed diabetes among adults aged >=18 years'  # Default value
    ),
    html.Button("Show Outliers", id="show-outliers-button", n_clicks=0),
    html.Div(
        dcc.Graph(id='choropleth-map'),
        style={'display': 'flex', 'justify-content': 'center'}
        ),
    html.Div(
        id='table-title1',
        children="Counties with Highest and Lowest Rates:",
        style={'fontSize': 24, 'fontWeight':'bold','textAlign': 'center'}
    ),
    html.Div(id='table-title', children="Selected Measure", style={'fontSize': 24, 'fontWeight':'bold','marginBottom': 20, 'textAlign': 'center'}),
    
    html.Div(
        dash_table.DataTable(
            id='outliers-table',
            columns=[
                {"name": "County", "id": "County"},
                {"name": "State", "id": "State"},
                {"name": "Percent", "id": "Percent"},
            ],        data=[],
            style_cell=table_style_cell,  # Apply cell style
            style_header=table_style_header,  # Apply header style
            style_data_conditional=[],
            style_table={'overflowX': 'auto', 'width': '500px'},
            style_cell_conditional=[
                {'if': {'column_id': 'County'}, 'width': '55%'},  # Adjust width for County column
                {'if': {'column_id': 'State'}, 'width': '35%'},  # Adjust width for State column
                {'if': {'column_id': 'Percent'}, 'width': '15%'},  # Adjust width for Percent column
            ],
        ),
        style={'display': 'flex', 'justify-content': 'center'}  
    )

])

def find_top_bottom_values(data_series, max_values):
    # Sort the data series
    sorted_data = data_series.sort_values()

    # Select the top and bottom values
    bottom_values = sorted_data.head(max_values)
    top_values = sorted_data.tail(max_values)

    # Keep track of the indices
    bottom_indices = bottom_values.index
    top_indices = top_values.index

    # Combine both top and bottom values
    combined_values = pd.concat([bottom_values, top_values])

    return combined_values, bottom_indices, top_indices



# Callback to update map based on dropdown selection and button click
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('measure-dropdown', 'value')]
)
def update_map(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]

    # Create the choropleth map
    fig = go.Figure(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df['FIPS'],
        z=filtered_df['Data_Value'],
        colorscale="RdYlGn_r",
        hovertemplate='%{customdata[0]} County, %{customdata[1]}<br>' + selected_measure + ': %{z:.2%}',
        customdata=filtered_df[['LocationName', 'StateAbbr']],
        colorbar=dict(thickness=10, len=0.5, tickformat=".0%"),
        zmin=filtered_df['Data_Value'].min(),
        zmax=filtered_df['Data_Value'].max(),
        showscale=True,
        name=""
    ))

    fig.update_layout(
        geo=dict(scope="usa"),
        margin={"r": 0, "l": 0, "b": 0, "t": 0},
        title_text=selected_measure + ' by County',
        title_y=0.85,
        title_x=0.5,
        title_font=dict(size=20),
        width=1200,
        height=900
    )

    return fig

# Callback to toggle button label
@app.callback(
    Output('show-outliers-button', 'children'),
    [Input('show-outliers-button', 'n_clicks')]
)
def toggle_button_label(n_clicks):
    if n_clicks % 2 == 0:
        return "Show Outliers"
    else:
        return "Hide Outliers"
    
# Callback to update the outliers table
@app.callback(
    Output('outliers-table', 'data'),
    Output('outliers-table', 'style_data_conditional'),
    Output('outliers-table', 'columns'),
    Output('table-title', 'children'),  # Output for the title
    [Input('measure-dropdown', 'value'),
     Input('show-outliers-button', 'n_clicks')]
)

def update_table(selected_measure, n_clicks):
    if n_clicks % 2 == 1:
        filtered_df = df[df['Measure'] == selected_measure]
        outliers, _, _ = find_top_bottom_values(filtered_df['Data_Value'], max_values)
        outliers_df = filtered_df.loc[outliers.index]

        # Determine the min and max values for scaling
        min_val = outliers_df['Data_Value'].min()
        max_val = outliers_df['Data_Value'].max()

        # Apply color based on value BEFORE formatting as percentage
        outliers_df['Color'] = outliers_df['Data_Value'].apply(lambda x: value_to_color(x, min_val, max_val))

        # Format Data_Value as percentage and rename columns
        outliers_df['Data_Value'] = outliers_df['Data_Value'].apply(lambda x: f"{x:.1%}")
        outliers_df.rename(columns={'LocationName': 'County', 'StateDesc': 'State', 'Data_Value': 'Percent'}, inplace=True)

        # Define columns for DataTable
        columns = [{"name": col, "id": col} for col in ['County', 'State', 'Percent']]

        # Define style conditions using the Color column
        style = [{'if': {'row_index': i}, 'backgroundColor': color} for i, color in enumerate(outliers_df['Color'])]

        # Define title based on the selected measure
        title = f"{selected_measure}"

        return outliers_df[['County', 'State', 'Percent']].to_dict('records'), style, columns, title
    else:
        return [], [], [], ""


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)