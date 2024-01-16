import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

filepath_ranking_data = "data/interim/CDC_PLACES_county_rankings_by_year.pickle"
df = pd.read_pickle(filepath_ranking_data)  

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)

max_values = 10

def value_to_color(value, min_val, max_val, colormap=plt.cm.RdYlGn):
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
    html.Div(
        dcc.Graph(id='choropleth-map'),
        style={'display': 'flex', 'justify-content': 'center'}
        ),
    html.Div(
        id='table-title',
        style={'fontSize': 30, 'fontWeight':'bold','textAlign': 'center','marginBottom': 10}
    ),
    
    html.Div(
        dash_table.DataTable(
            id='ranking-table',
            columns=[
                {"name": "County", "id": "County"},
                {"name": "State", "id": "State"},
                {"name": "Score", "id": "Score"},
                {"name": "Rank", "id": "Rank"},

            ],        data=[],
            style_cell=table_style_cell,  # Apply cell style
            style_header=table_style_header,  # Apply header style
            style_data_conditional=[],
            style_table={'overflowX': 'auto', 'width': '500px'},
            style_cell_conditional=[
                {'if': {'column_id': 'County'}, 'width': '40%'},  # Adjust width for County column
                {'if': {'column_id': 'State'}, 'width': '30%'},  # Adjust width for State column
                {'if': {'column_id': 'Score'}, 'width': '15%'},  # Adjust width for Percent column
                {'if': {'column_id': 'Score'}, 'width': '15%'}
            ],
        ),
        style={'display': 'flex', 'justify-content': 'center'}  
    )

])

# Callback to update map based on dropdown selection and button click
@app.callback(
    Output('choropleth-map', 'figure'),
    [
     Input('year-dropdown', 'value')]
)
def update_map( selected_year):
    filtered_df = df[(df['Year'] == selected_year)]
    # Calculate the 10th and 90th percentiles of the data
    percentile_low = filtered_df['Weighted_Score_Normalized'].quantile(0.05)
    percentile_high = filtered_df['Weighted_Score_Normalized'].quantile(0.95)

    num_counties = len(filtered_df)
    # Create the choropleth map
    fig = go.Figure(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df['GEOID'],
        z=filtered_df['Weighted_Score_Normalized'],
        colorscale="RdYlGn",
        hovertemplate='%{customdata[0]} County, %{customdata[1]}<br>Score: %{z:.2f}<br>Rank: %{customdata[2]} of ' + str(num_counties),
        customdata=filtered_df[['LocationName', 'StateAbbr', 'Rank']],
        colorbar=dict(thickness=15, len=0.5, tickformat=".2"),
        zmin=percentile_low,
        zmax=percentile_high,
        showscale=True,
        name=""
    ))

    fig.update_layout(
        geo=dict(scope="usa"),
        margin={"r": 0, "l": 0, "b": 0, "t": 0},
        title_text=f"Overall Health Score by County for {selected_year}",
        title_y=0.85,
        title_x=0.5,
        title_font=dict(size=30),
        width=1200,
        height=900
    )
    fig.add_annotation(
    text="Color scale represents<br>5th to 95th percentile",
    align='left',
    showarrow=False,
    xref='paper', yref='paper',
    x=1.055, y=.21,  
    bgcolor="white",
    bordercolor="black",
    borderpad=4
    )

    return fig
    
# Callback to update the table table
@app.callback(
    Output('ranking-table', 'data'),
    Output('ranking-table', 'style_data_conditional'),
    Output('ranking-table', 'columns'),
    Output('table-title', 'children'),  # Output for the title
    [
     Input('year-dropdown', 'value'),  # Include year-dropdown as an input
     ]
)
def update_table(selected_year):
    # Filter by year
    ranking_table_df = df[(df['Year'] == selected_year)]

    # Get the total number of ranks for the year to identify the bottom ranks
    max_rank = ranking_table_df['Rank'].max()

    # Select top 10 and bottom 10 ranks
    top_ranks = ranking_table_df[ranking_table_df['Rank'] <= 10]
    bottom_ranks = ranking_table_df[ranking_table_df['Rank'] > max_rank - 10]

    # Combine top and bottom ranks
    combined_ranks_df = pd.concat([top_ranks, bottom_ranks]).sort_values(by='Rank')

    # Determine the min and max values for scaling
    min_val = combined_ranks_df['Weighted_Score_Normalized'].min()
    max_val = combined_ranks_df['Weighted_Score_Normalized'].max()

    # Apply color based on value BEFORE formatting as percentage
    combined_ranks_df['Color'] = combined_ranks_df['Weighted_Score_Normalized'].apply(lambda x: value_to_color(x, min_val, max_val))

    # Format Weighted_Score_Normalized as a rounded number and rename columns
    combined_ranks_df['Weighted_Score_Normalized'] = round(combined_ranks_df['Weighted_Score_Normalized'], 2)
    combined_ranks_df.rename(columns={'LocationName': 'County', 'StateDesc': 'State', 'Weighted_Score_Normalized': 'Score'}, inplace=True)

    # Define columns for DataTable
    columns = [{"name": col, "id": col} for col in ['County', 'State', 'Score', 'Rank']]

    # Define style conditions using the Color column
    style = [{'if': {'row_index': i}, 'backgroundColor': color} for i, color in enumerate(combined_ranks_df['Color'])]

    # Define title based on the year
    title = f"County Rank of Overall Health Metrics for {selected_year}"

    return combined_ranks_df[['County', 'State', 'Score', 'Rank']].to_dict('records'), style, columns, title

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)