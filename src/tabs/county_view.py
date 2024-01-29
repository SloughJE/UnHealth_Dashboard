import pandas as pd
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


def create_county_econ_charts(df_bea, fips_county='01011'):

    df_bea_county = df_bea[(df_bea.GeoFips==fips_usa) | (df_bea.GeoFips==fips_county)]

    # CPI Adjusted per Capita Income
    traces = []
    for geo_name in df_bea_county['GeoName'].unique():
        trace = go.Scatter(x=df_bea_county[df_bea_county['GeoName'] == geo_name]['TimePeriod'],
                        y=df_bea_county[(df_bea_county['GeoName'] == geo_name) & (df_bea_county.Statistic=='CPI Adjusted Per Capita Income')]['DataValue'],
                        mode='lines',
                        name=geo_name)
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='CPI Adjusted Income (~1983 dollars)<br>(counties adjusted with regional CPI)',
                    xaxis=dict(title='TimePeriod'),
                    yaxis=dict(title='CPI Adjusted Per Capita Income'),
                    template='plotly_dark')  # Set the dark theme

    # Create the figure
    fig_adj_income = go.Figure(data=traces, layout=layout)

    
    # Per Capita Income
    #######
    traces = []
    for geo_name in df_bea_county['GeoName'].unique():
        trace = go.Scatter(x=df_bea_county[df_bea_county['GeoName'] == geo_name]['TimePeriod'],
                        y=df_bea_county[(df_bea_county['GeoName'] == geo_name) & (df_bea_county.Statistic=='Per capita personal income')]['DataValue'],
                        mode='lines',
                        name=geo_name)
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='Current Dollar Income',
                    xaxis=dict(title='TimePeriod'),
                    yaxis=dict(title='Income'),
                    template='plotly_dark')  # Set the dark theme

    # Create the figure
    fig_income = go.Figure(data=traces, layout=layout)

    # Adj GDP per Capita
    ##########################

    traces = []
    df_chart = df_bea_county[df_bea_county.Statistic=='Real GDP Per Capita']
    for geo_name in df_chart['GeoName'].unique():
        trace = go.Scatter(x=df_chart[df_chart['GeoName'] == geo_name]['TimePeriod'],
                        y=df_chart[(df_chart['GeoName'] == geo_name)]['DataValue'],
                        mode='lines',
                        name=geo_name)
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='Adjusted GDP per Capita (2017 dollars)',
                    xaxis=dict(title='TimePeriod'),
                    yaxis=dict(title='Adjusted GDP'),
                    template='plotly_dark')  # Set the dark theme

    # Create the figure
    fig_real_gdp = go.Figure(data=traces, layout=layout)

    # Current Dollar GDP per Capita
    #################

    traces = []
    df_chart = df_bea_county[df_bea_county.Statistic=='Current-dollar GDP Per Capita']
    for geo_name in df_chart['GeoName'].unique():
        trace = go.Scatter(x=df_chart[df_chart['GeoName'] == geo_name]['TimePeriod'],
                        y=df_chart[(df_chart['GeoName'] == geo_name)]['DataValue'],
                        mode='lines',
                        name=geo_name)
        traces.append(trace)

    # Create the layout
    layout = go.Layout(title='Current Dollar GDP per Capita',
                    xaxis=dict(title='TimePeriod'),
                    yaxis=dict(title='Adjusted Income'),
                    template='plotly_dark')  # Set the dark theme

    # Create the figure
    fig_gdp = go.Figure(data=traces, layout=layout)
    
    return fig_adj_income, fig_income, fig_real_gdp, fig_gdp



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
                        subplot_titles=('County Health Metrics',
                                        'Contribution to CHS'),
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
        text=f"Total: {total}",
        showarrow=False,
        font=dict(size=16, color="white"),
        bgcolor="rgba(0,0,0,0.5)",
        borderpad=4,
        xanchor="center"
    )


    fig.update_layout(
        title={
            'text': f"{sorted_df.iloc[0].LocationName}, {sorted_df.iloc[0].StateAbbr}",
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

    fig.update_xaxes(title_text="Percent Occurrence", row=1, col=1)
    fig.update_yaxes(title_text="", row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=2)
    fig.update_yaxes(title_text="Contribution to CHS", row=1, col=2)

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
    
    filtered_df = df_ranking[(df_ranking['StateAbbr'] == selected_state) & (df_ranking['LocationName'] == selected_county)]

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df['GEOID'],
        z=filtered_df.Weighted_Score_Normalized,
        colorscale="RdYlGn_r",
        customdata=filtered_df[['GEOID', 'LocationName', 'StateAbbr', 'Rank', 'Weighted_Score_Normalized']],
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
        title_text='Health Score for ' + selected_county + ', ' + selected_state,
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