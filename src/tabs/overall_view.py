
import plotly.graph_objects as go
import pandas as pd
import json

from pygam import LinearGAM, s
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


### Load data#####
df_ranking = pd.read_pickle("data/processed/CDC_PLACES_county_rankings.pickle")
#df_ranking = df_ranking[df_ranking.Year==2020]
num_counties = len(df_ranking)

df_bea = pd.read_pickle("data/processed/bea_economic_data.pickle")
df_bea = df_bea[(df_bea.TimePeriod==2022) & (df_bea.State.notnull()) & ((df_bea.Statistic=='Population') | (df_bea.Statistic=='Real GDP Per Capita'))]

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)
############

def check_fips_county_data(df_bea, df_ranking):
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
    
    # Add columns for matched_GEOID and Note to df_ranking
    df_ranking['matched_GEOID'] = df_ranking['GEOID']
    df_ranking['Note'] = ''

    # Process each row in df_ranking
    for index, row in df_ranking.iterrows():
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
                df_ranking.at[index, 'matched_GEOID'] = matching_rows.GeoFips.iloc[0]
                df_ranking.at[index, 'Note'] = f"Updated to {matching_rows.GeoName.iloc[0]}"

check_fips_county_data(df_bea, df_ranking)
# Extract necessary columns from df_bea
df_bea_pivot = df_bea.pivot(index='GeoFips', columns='Statistic', values='DataValue')

# Merge the DataFrames
# Assuming df_bea_pivot has GeoFips as an index
df_ranking = pd.merge(df_ranking, df_bea_pivot, left_on='matched_GEOID', right_index=True, how='left')

print(df_ranking[df_ranking.LocationName=="Albemarle"])
df_gam = df_ranking[['GEOID','LocationName','StateDesc','StateAbbr','Weighted_Score_Normalized', 'Rank','Population','Real GDP Per Capita','Note']]

# Calculate IQR for 'Real GDP Per Capita'

percentile_low = df_ranking['Weighted_Score_Normalized'].quantile(0.05)
percentile_high = df_ranking['Weighted_Score_Normalized'].quantile(0.95)
percentile_low_scatter = percentile_low
percentile_high_scatter = percentile_high
####################
####BUBBLE CHART####
####################


# FILTER outliers based on IQR
def filter_outliers(df):
        
    Q1 = df['Real GDP Per Capita'].quantile(0.01)
    Q3 = df['Real GDP Per Capita'].quantile(0.99)
    IQR = Q3 - Q1

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out outliers
    df = df[(df['Real GDP Per Capita'] >= lower_bound) & (df['Real GDP Per Capita'] <= upper_bound)]
    df['Weighted_Score_Normalized'] = round(df.Weighted_Score_Normalized,2)
    
    return df

def fit_gam(df):
    # Fit a GAM model
    gam = LinearGAM(s(0, n_splines=20, constraints='monotonic_dec', lam=10))
    gam.fit(df[['Real GDP Per Capita']], df['Weighted_Score_Normalized'])

    # Generate predictions and intervals as before
    x_pred = pd.DataFrame({'Real GDP Per Capita': np.linspace(df['Real GDP Per Capita'].min(), df['Real GDP Per Capita'].max(), 500)})
    y_pred = gam.predict(x_pred)
    y_intervals = gam.prediction_intervals(x_pred, width=0.8)

    return x_pred, y_pred, y_intervals

df_gam = filter_outliers(df_gam)
x_pred, y_pred, y_intervals = fit_gam(df_gam)


def create_updated_bubble_chart(df,selected_state,x_pred, y_pred, y_intervals):

    # Always start with the full dataset
    filtered_df = df.copy()

    # Step 1: Filter by State (if any are selected)
    if selected_state:
        filtered_df = filtered_df[filtered_df['StateAbbr'].isin(selected_state)]

    hover_text = [
        f"{row['LocationName']}, {row['StateDesc']}<br>County Health Score: {row['Weighted_Score_Normalized']}<br>Rank: {row['Rank']:,.0f}<br>GDP Per Capita: {row['Real GDP Per Capita']:,.0f}<br>Population: {row['Population']:,.0f}"
        for index, row in filtered_df.iterrows()
    ]

    
    fig_bubble = go.Figure()
    # Check if there is data after filtering
    if len(filtered_df) == 0:
        # If no data, display a message
        fig_bubble.update_layout(
            xaxis={'visible': False},  # Hide x axis
            yaxis={'visible': False},  # Hide y axis
            annotations=[
                {
                    'text': 'No data available for this state or county',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20}
                }
            ],
            paper_bgcolor="black",  # Background color
            plot_bgcolor="black",  # Plot area background color
            font=dict(color="white"),  # Text color
        )
    else:
        scatter_plot = go.Scatter(
            x=filtered_df['Real GDP Per Capita'],
            y=filtered_df['Weighted_Score_Normalized'],
            mode='markers',
            marker=dict(
                color=list(filtered_df['Weighted_Score_Normalized']),  # The variable for color scale
                colorscale='RdYlGn_r',  # Red-Yellow-Green color scale
                cmin=percentile_low_scatter,  # 5th percentile
                cmax=percentile_high_scatter,  # 95th percentile
                line=dict(
                    width=.2,
                    color='black'
                )
            ),
            text=hover_text,
            hoverinfo='text',
            customdata=filtered_df['GEOID'],
            name='County'
        )


        # Add the GAM trend line
        trend_line = go.Scatter(x=x_pred['Real GDP Per Capita'], y=y_pred, mode='lines', 
                                name='GAM Trend Line', 
                                line=dict(color='darkgrey', width=5))

        # Add prediction intervals
        lower_interval = go.Scatter(
            x=x_pred['Real GDP Per Capita'],
            y=y_intervals[:, 0],
            mode='lines',
            line=dict(color='lightgrey', width=1, dash='dot'),  # Lighter color, dashed line
            name='Lower Interval',
            showlegend=False
        )

        upper_interval = go.Scatter(
            x=x_pred['Real GDP Per Capita'],
            y=y_intervals[:, 1],
            fill='tonexty',
            mode='lines',
            line=dict(color='lightgrey', width=1, dash='dot'),  # Lighter color, dashed line
            name='95% Prediction Interval',
            fillcolor='rgba(150, 150, 150, 0.3)',  # Light fill color with reduced opacity
            showlegend=True
        )

        fig_bubble.add_trace(scatter_plot)
        fig_bubble.add_trace(lower_interval)
        fig_bubble.add_trace(upper_interval)
        fig_bubble.add_trace(trend_line)

        # Update the layout for a dark and minimalist theme
        fig_bubble.update_layout(
            title='GDP per Capita vs Health Score',
            title_x=0.5,  # Center the title
            title_font=dict(size=20),  # Adjust the font size if needed
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(title='GDP per capita 2020', range=[0, 200000], showgrid=False, linecolor='darkgrey', linewidth=1),  # Hide grid lines and set axis line color
            yaxis=dict(range=[0, 101], showgrid=False, linecolor='darkgrey', linewidth=1),  # Hide grid lines and set axis line color
            yaxis_title='Health Score',
            #width=700, height=600,
            coloraxis_showscale=False,
            
            legend=dict(
                x=0.74,
                y=.90,
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="white"
                ),
                bordercolor="gray",
                borderwidth=1
            ),
            paper_bgcolor="black",  # Background color
            plot_bgcolor="black",  # Plot area background color
            font=dict(color="white"),  # Text color
        )

    fig_bubble.update_layout(
        autosize=True,  # Enable autosize
    )
    return fig_bubble


####################
###### MAP #########
####################

def create_updated_map(df, selected_state):
    
    # Filter the dataframe based on selected_state (if it's not None)
    if selected_state is not None and len(selected_state) > 0:
        filtered_df_by_state = df[df['StateAbbr'].isin(selected_state)]
    else:
        filtered_df_by_state = df  # No state filter applied

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df_by_state['GEOID'],
        z=filtered_df_by_state.Weighted_Score_Normalized,
        colorscale="RdYlGn_r",
        customdata=filtered_df_by_state[['GEOID', 'LocationName', 'StateAbbr', 'Rank', 'Weighted_Score_Normalized']],
        hovertemplate = '%{customdata[1]} County, %{customdata[2]}<br>Score: %{customdata[4]:.2f}<br>Rank: %{customdata[3]} of ' + str(num_counties),
        marker_line_width=0,
        colorbar=dict(
            thickness=15,
            len=0.5,
            tickformat="0",
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
        title_text='Health Score',
        title_x=0.5,  # Center the title
        margin=dict(l=0, r=0, t=40, b=0),
        title_font=dict(size=20, color='white'),
        
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
available_states = df_ranking['StateAbbr'].unique()
available_states.sort()

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

