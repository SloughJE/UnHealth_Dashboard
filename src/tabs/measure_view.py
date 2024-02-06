
import plotly.graph_objects as go
import pandas as pd
import json

import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


### Load data#####
df_measures = pd.read_pickle("data/processed/df_measures_final.pickle")

num_counties = df_measures.GEOID.nunique()

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)
############


####################
###### MAP #########
####################

def create_updated_map_measures(df, selected_state, selected_measure):
    
    filtered_df = df[(df['Measure_short'] == selected_measure)]
    # Calculate the 10th and 90th percentiles of the data
    percentile_low = filtered_df['Data_Value'].quantile(0.05)
    percentile_high = filtered_df['Data_Value'].quantile(0.95)
    
    # Filter the dataframe based on selected_state (if it's not None)
    if selected_state is not None and len(selected_state) > 0:
        filtered_df_by_state = filtered_df[filtered_df['StateDesc'].isin(selected_state)]
    else:
        filtered_df_by_state = filtered_df  # No state filter applied

    fig = go.Figure()



    # Create the choropleth map
    fig = go.Figure(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df_by_state['GEOID'],
        z=filtered_df_by_state['Data_Value'],
        colorscale="RdYlGn_r",
        hovertemplate='%{customdata[0]} County, %{customdata[1]}<br>' + selected_measure + ': %{z:.2%}<br>Year obtained: %{customdata[2]}',
        customdata=filtered_df_by_state[['LocationName', 'StateDesc','Year']],
        #colorbar=dict(thickness=15, len=0.5, tickformat=".1%"),
        marker_line_width=0,
        colorbar=dict(
            thickness=15,
            len=0.5,
            tickformat=".1%",
            x=0.05,  # Adjust this value to move the colorbar closer
            xpad=0,  # Adjust padding if needed
            tickfont=dict(color='white'),  # Set tick font color
        ),
        zmin=percentile_low,
        zmax=percentile_high,
        showscale=True,
        name=""
        )
    )

    fig.update_layout(
        height=600,
        geo=dict(
            scope="usa",
            lakecolor='black',
            landcolor='black',
            bgcolor='black',
            subunitcolor='darkgrey',
            showlakes=True,
            showsubunits=True,
            showland=True,
            showcountries=False,
            showcoastlines=True,
            countrycolor='darkgrey',
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        title_text=f'Percent: {selected_measure}',
        title_x=0.5,  # Center the title
        margin=dict(l=0, r=0, t=40, b=0),
        title_font=dict(size=24, color='white'),
        
    )

    fig.add_annotation(
        text="Color scale represents<br>5th to 95th percentile",
        align='left',
        showarrow=False,
        xref='paper', yref='paper',
        x=0.95, y=0.15,
        bgcolor="black",  # Set background color
        bordercolor="gray",  # Set border color
        borderpad=4,
        font=dict(color='white')  # Set text color
    )

    fig.update_layout(
        autosize=True,  # Enable autosize
        #margin=dict(l=0, r=0, t=0, b=0)  # Remove margin
    )
    return fig



# Extract unique states and counties from your data
available_states = df_measures['StateDesc'].unique()
available_states.sort()

# Extract unique states and counties from your data
available_measures = df_measures['Measure_short'].unique()
available_measures.sort()

def find_top_bottom_values(df, column_name, max_values):
    # Sort the DataFrame based on a column
    sorted_df = df.sort_values(by=column_name)

    # Select the top and bottom values
    bottom_df = sorted_df.head(max_values)
    top_df = sorted_df.tail(max_values)

    # Combine both top and bottom DataFrames
    combined_df = pd.concat([bottom_df, top_df])

    return combined_df

def value_to_color(value, min_val, max_val, colormap=plt.cm.RdYlGn_r):
    """Convert a value to a color using a matplotlib colormap."""
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
    return mcolors.to_hex(colormap(norm(value)))

