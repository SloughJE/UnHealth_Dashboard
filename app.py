import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# filepath_health_data = "data/interim/health_food_2020_GEOID.pickle"
filepath_health_data = "data/interim/CDC_PLACES_GEOID.pickle"
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
    id='year-dropdown',
    options=[{'label': year, 'value': year} for year in sorted(df['Year'].unique())],
    value=df['Year'].max()
    ),
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

# YEAR CALLBACK
@app.callback(
    Output('measure-dropdown', 'options'),
    [Input('year-dropdown', 'value')]
)
def set_measure_options(selected_year):
    # Filter the DataFrame based on the selected year
    filtered_df = df[df['Year'] == selected_year]
    # Return the unique measures for this year
    return [{'label': measure, 'value': measure} for measure in filtered_df['Measure'].unique()]


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
    [Input('measure-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_map(selected_measure, selected_year):
    print(selected_year)
    filtered_df = df[(df['Measure'] == selected_measure) & (df['Year'] == selected_year)]
    # Calculate the 10th and 90th percentiles of the data
    percentile_low = filtered_df['Data_Value'].quantile(0.05)
    percentile_high = filtered_df['Data_Value'].quantile(0.95)
    print(selected_measure)
    print(percentile_low)
    print(percentile_high)

    # Create the choropleth map
    fig = go.Figure(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df['GEOID'],
        z=filtered_df['Data_Value'],
        colorscale="RdYlGn_r",
        hovertemplate='%{customdata[0]} County, %{customdata[1]}<br>' + selected_measure + ': %{z:.2%}',
        customdata=filtered_df[['LocationName', 'StateAbbr']],
        colorbar=dict(thickness=15, len=0.5, tickformat=".1%"),
        zmin=percentile_low,
        zmax=percentile_high,
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
    fig.add_annotation(
    text="Color scale represents<br>5th to 95th percentile",
    align='left',
    showarrow=False,
    xref='paper', yref='paper',
    x=1.075, y=.21,  # Adjust the position according to your layout
    bgcolor="white",
    bordercolor="black",
    borderpad=4
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
     Input('year-dropdown', 'value'),  # Include year-dropdown as an input
     Input('show-outliers-button', 'n_clicks')]
)
def update_table(selected_measure, selected_year, n_clicks):  # Include selected_year as a parameter
    if n_clicks % 2 == 1:
        # Filter by both measure and year
        filtered_df = df[(df['Measure'] == selected_measure) & (df['Year'] == selected_year)]
        filtered_df = filtered_df[filtered_df['LocationName'] != filtered_df['StateDesc']]

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
        title = f"{selected_measure} for {selected_year}"

        return outliers_df[['County', 'State', 'Percent']].to_dict('records'), style, columns, title
    else:
        return [], [], [], ""


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)