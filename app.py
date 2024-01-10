import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import json

filepath_health_data = "data/interim/health_food_2020.pickle"
df = pd.read_pickle(filepath_health_data)  
df['Data_Value'] = df['Data_Value'] / 100

# GeoJSON file
file_path_geo_json = "data/interim/plotly_geojson-counties-fips.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)
# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Dropdown(
        id='measure-dropdown',
        options=[{'label': i, 'value': i} for i in df['Measure'].unique()],
        value='Diagnosed diabetes among adults aged >=18 years'  # Default value
    ),
    dcc.Graph(id='choropleth-map')
])

# Callback to update map based on dropdown selection
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('measure-dropdown', 'value')]
)
def update_map(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    print(filtered_df.head())
    print(filtered_df.Data_Value.isna().sum())

    # Create the choropleth map
    fig = go.Figure(go.Choropleth(
        geojson=counties,
        featureidkey="id",
        locations=filtered_df['FIPS'],
        z=filtered_df['Data_Value'],
        colorscale="RdYlGn_r",
        hovertemplate='%{customdata[0]} County, %{customdata[1]}<br>' + selected_measure + ': %{z:.2%}',  # Display as percentages
        customdata=filtered_df[['LocationName', 'StateAbbr']],
        colorbar=dict(thickness=10,len=0.5,tickformat=".0%"),
        zmin=filtered_df['Data_Value'].min(),
        zmax=filtered_df['Data_Value'].max(),
        showscale=True,  # Remove the color scale
        name=""  # Set a custom label
    ))
    
    fig.update_layout(
        geo=dict(scope="usa"),
        margin={"r": 0, "l": 0, "b": 0, "t": 0},
        title_text=selected_measure + ' by County',
        title_y=0.85,
        title_x=0.5,
        title_font=dict(size=20),
        width=1000,
        height=800
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
