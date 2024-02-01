
import plotly.graph_objects as go
import pandas as pd
import json

import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


### Load data#####
df_measures = pd.read_pickle("data/processed/CDC_PLACES_county_measures.pickle")
df_measures = df_measures[['GEOID','Year','StateDesc','LocationName','Category','Data_Value', 'Measure_short']]
df_measures['County Measure Rank'] = df_measures.groupby('Measure_short')['Data_Value'].rank(ascending=True, method='min')
df_measures['Data_Value'] = df_measures['Data_Value']/100
num_counties = df_measures.GEOID.nunique()

df_bea = pd.read_pickle("data/processed/bea_economic_data.pickle")
df_bea = df_bea[(df_bea.TimePeriod==2022) & (df_bea.State.notnull()) & ((df_bea.Statistic=='Population') | (df_bea.Statistic=='Per capita personal income'))]

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)
############

def check_fips_county_data(df_bea, df_measures):
    # map full state name to abbr
    state_mapping = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
            "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
            "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
            "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
            "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
            "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
            "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
            "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
            "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
            "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
        }
    
    # Add columns for matched_GEOID and Note to df_measures
    df_measures['matched_GEOID'] = df_measures['GEOID']
    df_measures['Note'] = ''

    # Process each row in df_measures
    for index, row in df_measures.iterrows():
        fips_county = row['GEOID']
        selected_state = row['StateDesc']
        selected_county = row['LocationName']

        # Check if FIPS code exists in the dataset
        if len(df_bea[df_bea.GeoFips == fips_county]) == 0:
            selected_state_abbr = state_mapping[selected_state]
            # Filter by selected state
            df_bea_find_fips = df_bea[df_bea.State == selected_state_abbr]
            
            # Try finding the county using the full selected_county name
            matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(selected_county, case=False, na=False)]
            
            # If not found, split the selected_county and try with the first part
            if matching_rows.empty and ' ' in selected_county:
                first_part_of_county = selected_county.split(' ')[0]
                matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(first_part_of_county, case=False, na=False)]
            
            # Update matched_GEOID if a match is found
            if not matching_rows.empty:
                df_measures.at[index, 'matched_GEOID'] = matching_rows.GeoFips.iloc[0]
                df_measures.at[index, 'Note'] = f"Econ data from {matching_rows.GeoName.iloc[0]}"

#check_fips_county_data(df_bea, df_measures)
# Extract necessary columns from df_bea
df_bea_pivot = df_bea.pivot(index='GeoFips', columns='Statistic', values='DataValue')

# Merge the DataFrames
# Assuming df_bea_pivot has GeoFips as an index
#df_measures = pd.merge(df_measures, df_bea_pivot, left_on='matched_GEOID', right_index=True, how='left')


####################
###### MAP #########
####################

def create_updated_map(df, selected_state, selected_measure):
    
    filtered_df = df[(df['Measure_short'] == selected_measure)]
    # Calculate the 10th and 90th percentiles of the data
    percentile_low = filtered_df['Data_Value'].quantile(0.05)
    percentile_high = filtered_df['Data_Value'].quantile(0.95)
    print(selected_measure)
    print(percentile_low)
    print(percentile_high)
    
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

