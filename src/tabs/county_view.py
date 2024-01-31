import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


fips_usa = '00000'
fips_county = '01011'

df_bea = pd.read_pickle("data/processed/bea_economic_data.pickle")
df_all_counties = pd.read_pickle("data/processed/CDC_PLACES_county_measures.pickle")
df_ranking = pd.read_pickle("data/processed/CDC_PLACES_county_rankings.pickle")

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)



health_score_explanation = """
The Health Score provides a comprehensive overview of a county's health by combining data on various health indicators, such as the prevalence of chronic diseases, lifestyle factors, and disabilities. Each indicator is assigned an impact score, reflecting its significance on public health. High-impact indicators include stroke, diabetes, and cancer, among others, while lower-impact indicators cover aspects like sleep duration and health screenings.

The process involves normalizing data across all indicators to create a score out of 100, where a higher score signals more significant health challenges within the county. This normalized score allows for direct comparison across counties, offering insights into areas needing most health-related interventions and support.
"""

def check_fips_county_data(df_bea, fips_county, selected_state, selected_county):
    
    # Check if FIPS code exists in the dataset
    if len(df_bea[df_bea.GeoFips == fips_county]) == 0:
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
        selected_state_abbr = state_mapping[selected_state]
        # Filter by selected state
        df_bea_find_fips = df_bea[df_bea.State == selected_state_abbr]
        
        # Try finding the county using the full selected_county name
        matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(selected_county, case=False, na=False)]
        
        # If not found, split the selected_county and try with the first part
        if matching_rows.empty and ' ' in selected_county:
            first_part_of_county = selected_county.split(' ')[0]
            matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(first_part_of_county, case=False, na=False)]
        
        # Update fips_county if a match is found
        if not matching_rows.empty:
            fips_county = matching_rows.GeoFips.iloc[0]

    return fips_county


def create_county_econ_charts(df_bea_county):

    colors = ['#636efa', '#ef553b']  # Default colors for plotly_dark theme
    # CPI Adjusted per Capita Income
    traces = []
    for i, geo_name in enumerate(df_bea_county['GeoName'].unique()):
        trace = go.Scatter(x=df_bea_county[df_bea_county['GeoName'] == geo_name]['TimePeriod'],
                        y=df_bea_county[(df_bea_county['GeoName'] == geo_name) & (df_bea_county.Statistic=='CPI Adjusted Per Capita Income')]['DataValue'],
                        mode='lines',
                        name=geo_name,
                        line=dict(color=colors[i])
                        )
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='Income per Capita: CPI Adjusted (~1983 dollars, counties with regional CPI)',
                    xaxis=dict(title=''),
                    yaxis=dict(title='Income per Capita (adjusted)'),
                    template='plotly_dark',
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
                    )

    # Create the figure
    fig_adj_income = go.Figure(data=traces, layout=layout)

    
    # Per Capita Income
    #######
    traces = []
    for i, geo_name in enumerate(df_bea_county['GeoName'].unique()):
        trace = go.Scatter(x=df_bea_county[df_bea_county['GeoName'] == geo_name]['TimePeriod'],
                        y=df_bea_county[(df_bea_county['GeoName'] == geo_name) & (df_bea_county.Statistic=='Per capita personal income')]['DataValue'],
                        mode='lines',
                        name=geo_name,line=dict(color=colors[i]))
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='Income per Capita: Current Dollars',
                    xaxis=dict(title=''),
                    yaxis=dict(title='Income per Capita (current)'),
                    template='plotly_dark',
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
                    )

    # Create the figure
    fig_income = go.Figure(data=traces, layout=layout)

    # Adj GDP per Capita
    ##########################

    traces = []
    df_chart = df_bea_county[df_bea_county.Statistic=='Real GDP Per Capita']
    for i, geo_name in enumerate(df_bea_county['GeoName'].unique()):
        trace = go.Scatter(x=df_chart[df_chart['GeoName'] == geo_name]['TimePeriod'],
                        y=df_chart[(df_chart['GeoName'] == geo_name)]['DataValue'],
                        mode='lines',
                        name=geo_name,line=dict(color=colors[i]))
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='GDP per Capita: Adjusted (2017 dollars)',
                    xaxis=dict(title=''),
                    yaxis=dict(title='GDP per Capita (adjusted)'),
                    template='plotly_dark',
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
                    )

    # Create the figure
    fig_real_gdp = go.Figure(data=traces, layout=layout)

    # Current Dollar GDP per Capita
    #################

    traces = []
    df_chart = df_bea_county[df_bea_county.Statistic=='Current-dollar GDP Per Capita']
    for i, geo_name in enumerate(df_bea_county['GeoName'].unique()):
        trace = go.Scatter(x=df_chart[df_chart['GeoName'] == geo_name]['TimePeriod'],
                        y=df_chart[(df_chart['GeoName'] == geo_name)]['DataValue'],
                        mode='lines',
                        name=geo_name,line=dict(color=colors[i]))
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='GDP per Capita: Current Dollars',
                    xaxis=dict(title=''),
                    yaxis=dict(title='GDP per Capita (current)'),
                    template='plotly_dark',
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
                    )

    # Create the figure
    fig_gdp = go.Figure(data=traces, layout=layout)
    

    # Population, only the county
    df_chart = df_bea_county[(df_bea_county.Statistic=='Population') & (df_bea_county.GeoFips!="00000")]

    trace = go.Scatter(x=df_chart[df_chart['GeoName'] == geo_name]['TimePeriod'],
                    y=df_chart[(df_chart['GeoName'] == geo_name)]['DataValue'],
                    mode='lines',
                    name=geo_name,line=dict(color=colors[1]))

    # Create the layout
    layout = go.Layout(title=f'{geo_name} Population',
                    xaxis=dict(title=''),
                    yaxis=dict(title='Population'),
                    template='plotly_dark',
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
                    )

    # Create the figure
    fig_pop = go.Figure(data=trace, layout=layout)


    return fig_adj_income, fig_income, fig_real_gdp, fig_gdp, fig_pop



def create_county_health_charts(df_ranking,df_all_counties,fips_county='01011'):
    
    df_ranking_county = df_ranking[df_ranking.GEOID==fips_county]
    df_county_measures = df_all_counties[df_all_counties.GEOID==fips_county]

    # Assuming df_county is your DataFrame and it contains a 'Category' column
    categories = df_county_measures['Category'].unique()
    colors = px.colors.qualitative.Plotly  # Or any other color sequence you prefer

    # Map each category to a color
    color_scale = {category: color for category, color in zip(categories, colors)}

    sorted_df = df_county_measures.sort_values(by='absolute_contribution', ascending=False)

    # Group by 'Category' and sum the 'percent_contribution'
    grouped_df = df_county_measures.groupby('Category')['absolute_contribution'].sum().reset_index()

    # Sort the grouped DataFrame by 'percent_contribution' in ascending order
    sorted_grouped_df = grouped_df.sort_values(by='absolute_contribution', ascending=False)
    sorted_categories = sorted_grouped_df['Category'].tolist()

    sorted_df['Category'] = pd.Categorical(sorted_df['Category'], categories=sorted_categories, ordered=True)
    sorted_df = sorted_df.sort_values(by=['Category', 'Data_Value'], ascending=[True, True])
    ###################################

    fig = make_subplots(rows=1, cols=2, column_widths=[0.75, 0.25], 
                        subplot_titles=('CDC Health Survey',
                                        'Contribution by Category'),
                                        )

    # Map 'Category' to colors for the first chart
    colors_mapped = sorted_df['Category'].map(color_scale).tolist()

    # Add the first chart to the first column
    fig.add_trace(go.Bar(x=sorted_df['Data_Value'], y=sorted_df['Measure_short'],
                        orientation='h', marker_color=colors_mapped,
                        hovertemplate='%{y}: %{x:.2f}<br>Data Value: %{customdata:.2f}',
                        customdata=sorted_df['absolute_contribution'],
                        name='All County Metrics'),
                row=1, col=1)

    for category in sorted_categories:
        df_filtered = sorted_grouped_df[sorted_grouped_df['Category'] == category]
        fig.add_trace(go.Bar(y=df_filtered['absolute_contribution'], x=[1]*len(df_filtered),
                            name=category, marker_color=color_scale[category],
                            text=category, orientation='v'),
                    row=1, col=2)

    total = df_ranking_county['Weighted_Score_Normalized'].iloc[0].round(2)

    # Add an annotation for the total above the stacked bar chart
    fig.add_annotation(
        xref="x2",  # Referencing the x-axis of the second subplot
        yref="y2",  # Referencing the y-axis of the second subplot
        x=1,  # Centered on the x-axis for the stacked bar
        y=total + 1.7,  # Slightly above the top of the stacked bar
        text=f"Health Score: {total}",
        showarrow=False,
        font=dict(size=16, color="white"),
        bgcolor="rgba(0,0,0,0.5)",
        borderpad=4,
        xanchor="center"
    )


    fig.update_layout(
        title={
            'text': f"{sorted_df.iloc[0].LocationName}, {sorted_df.iloc[0].StateDesc}",
            #'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'size': 28,   # Set the font size here
                'family': "Arial, sans-serif",   # Optional: set the font family
                'color': "white"   # Optional: set the font color
            }
        },
        
        template='plotly_dark', showlegend=False, 
                    
                    barmode='stack',
                    margin=dict(t=150),)

    fig.update_xaxes(title_text="Percent", row=1, col=1)
    fig.update_yaxes(title_text="", row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=2)
    fig.update_yaxes(title_text="Health Score", row=1, col=2)

    fig.update_traces(textposition='inside', textangle=0, insidetextanchor='middle', 
                    textfont=dict(size=18), selector=dict(orientation='v'))

    return fig



##############
# County map
percentile_high = df_ranking['Weighted_Score_Normalized'].quantile(0.95)
percentile_low = df_ranking['Weighted_Score_Normalized'].quantile(0.05)
num_counties = len(df_ranking)

def create_county_map(selected_state, selected_county, df_ranking,counties):
    
    # Filter the dataframe based on selected_state and selected_county
    
    filtered_df = df_ranking[(df_ranking['StateDesc'] == selected_state) & (df_ranking['LocationName'] == selected_county)]

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df['GEOID'],
        z=filtered_df.Weighted_Score_Normalized,
        colorscale="RdYlGn_r",
        customdata=filtered_df[['GEOID', 'LocationName', 'StateDesc', 'Rank', 'Weighted_Score_Normalized']],
        hovertemplate='%{customdata[1]} County, %{customdata[2]}<br>Score: %{customdata[4]:.2f}<br>Rank: %{customdata[3]} of ' + str(num_counties) + '<extra></extra>',
        marker_line_width=0,
        colorbar=dict(
            thickness=15,
            len=0.5,
            tickformat="0",
            x=0.05,
            xpad=0,
            tickfont=dict(color='white'),
        ),
        zmin=percentile_low,
        zmax=percentile_high,
        showscale=True,
        name=""
    ))


    fig.update_geos(
        visible=True, 
        resolution=50,
        scope="usa",
        showsubunits=True,
        subunitcolor="Gray",
        showcountries=True,
        showcoastlines=True,
        fitbounds="locations",
    )

    fig.update_layout(
        geo=dict(
            scope="usa",
            lakecolor='black',
            landcolor='black',
            bgcolor='black',
            subunitcolor='darkgrey',
            showlakes=True,
            showland=True,
            showcountries=True,
            showcoastlines=True,
            countrycolor='darkgrey',
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        #title_text='Health Score for ' + selected_county + ', ' + selected_state,
        title_x=0.5,
        margin=dict(l=0, r=0, t=40, b=0),
        title_font=dict(size=20, color='white'),
    )

    # Add annotation if needed
    fig.add_annotation(
        text="Color scale represents<br>5th to 95th percentile",
        align='left',
        showarrow=False,
        xref='paper', yref='paper',
        x=0.95, y=0.15,
        bgcolor="black",
        bordercolor="gray",
        borderpad=4,
        font=dict(color='white')
    )

    fig.update_layout(autosize=False)

    return fig


def calculate_percent_difference_econ(df_bea_county, year_bea):
    # Filter data for the selected county and year 2022
    county_data = df_bea_county[(df_bea_county['GeoFips'] != "00000") & (df_bea_county['TimePeriod'] == year_bea)]

    # Filter data for the USA and year 2022
    usa_data = df_bea_county[(df_bea_county['GeoFips'] == '00000') & (df_bea_county['TimePeriod'] == year_bea)]

    def get_value(data, statistic):
        value = data[data['Statistic'] == statistic]['DataValue'].values
        return value[0] if value.size > 0 else None

    # Retrieve values for GDP and income for both county and USA
    county_gdp = get_value(county_data, 'Real GDP Per Capita')
    county_income = get_value(county_data, 'Per capita personal income')
    usa_gdp = get_value(usa_data, 'Real GDP Per Capita')
    usa_income = get_value(usa_data, 'Per capita personal income')

    # Function to calculate percent difference
    def percent_difference(local, national):
        if local is None or national is None:
            return None
        return round(((local - national) / national) * 100, 2)

    # Calculate percent differences
    gdp_percent_difference = percent_difference(county_gdp, usa_gdp)
    income_percent_difference = percent_difference(county_income, usa_income)
    
    return gdp_percent_difference, income_percent_difference

