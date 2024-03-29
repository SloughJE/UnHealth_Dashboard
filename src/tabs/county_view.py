import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import html
import dash_bootstrap_components as dbc

fips_usa = '00000'
fips_county = '01011'

df_bea = pd.read_pickle("data/processed/bea_economic_data.pickle")
df_all_counties = pd.read_pickle("data/processed/df_measures_final.pickle")
df_ranking_cv = pd.read_pickle("data/processed/df_summary_final.pickle")

# GeoJSON file
file_path_geo_json = "data/processed/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)

def create_kpi_layout(df_ranking_cv, fips_county, df_bea_county, fips_county_bea,health_score_explanation):

    # Get the corresponding GeoName for fips_county_bea
    geo_name_bea = df_bea[df_bea.GeoFips == fips_county_bea].GeoName.iloc[0] if not df_bea[df_bea.GeoFips == fips_county_bea].empty else "Unknown"
    # Check if fips_county and fips_county_bea are different
    if fips_county != fips_county_bea:
        note = html.P(f"Note: Economic data displayed is based on {geo_name_bea} (FIPS: {fips_county_bea}) due to data availability.", style={'color': 'yellow'})
    else:
        note = html.P()


    selected_data = df_ranking_cv[df_ranking_cv.GEOID==fips_county].iloc[0]
    county_name = selected_data['LocationName']
    state_name = selected_data['StateDesc']
    health_metric = selected_data['Weighted_Score_Normalized']
    rank = selected_data['Rank']

    year_bea = 2022
    gdp_percent_difference, income_percent_difference = calculate_percent_difference_econ(df_bea_county, year_bea)
    
    # Function to format the text
    def format_text(label, value):
        return f"{label} ({year_bea}): {value:.2f}%" if value is not None else f"{label} ({year_bea}): Not Available"

    # Format the percent differences
    gdp_percent_text = format_text("GDP per Capita % Diff. from USA Avg.", gdp_percent_difference)
    income_percent_text = format_text("Income per Capita % Diff. from USA Avg.", income_percent_difference)

    # Get population for the year and format it
    pop_county = df_bea_county[(df_bea_county.Statistic == 'Population') & (df_bea_county.GeoFips == fips_county_bea) & (df_bea_county.TimePeriod == year_bea)].DataValue.iloc[0]
    pop_county_formatted = "{:,}".format(int(pop_county))
        
    info_icon = html.I(className="bi bi-info-circle", id="health-score-tooltip-target", style={'cursor': 'pointer','font-size': '22px'})
    health_score_with_icon = html.H3(
        ["UnHealth Score™ ", info_icon],
        style={'color': 'white'}
    )
    health_score_tooltip = dbc.Tooltip(
        health_score_explanation,
        target="health-score-tooltip-target",
        placement="right",
        className='custom-tooltip',
        style={'white-space': 'pre-line'}
    )
    kpi_layout = html.Div([
        html.Div([
            health_score_with_icon,
            html.P(f"{health_metric:.2f} (out of 100)", style={'color': 'white', 'font-size': '1.2em'}),
            html.H3("Rank", style={'color': 'white'}),
            html.P(f"{rank} of {len(df_ranking_cv)}", style={'color': 'white', 'font-size': '1.2em'}),
        ], className='kpi-box-health-rank-box'),

        html.Div([
            html.H3("Economic Data", style={'color': 'white'}),
            html.P(gdp_percent_text, style={'color': 'white', 'font-size': '1.2em'}),
            html.P(income_percent_text, style={'color': 'white', 'font-size': '1.2em'}),
        ], className='kpi-box'),
        html.Div([
            html.H3("Population", style={'color': 'white'}),
            html.P(f"{pop_county_formatted} ({year_bea})", style={'color': 'white', 'font-size': '1.2em'}),
        ], className='kpi-box'),
        note
    ], className='kpi-container')

    return html.Div([kpi_layout, health_score_tooltip]) 


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
    layout = go.Layout(title='Income per Capita:<br>CPI Adjusted (~1983 dollars, counties with regional CPI)',
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
    layout = go.Layout(title='Income per Capita:<br>Current Dollars',
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
    layout = go.Layout(title='GDP per Capita:<br>Adjusted (2017 dollars)',
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
    layout = go.Layout(title='GDP per Capita:<br>Current Dollars',
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



def create_county_health_charts(df_ranking_cv,df_all_counties,fips_county='01011'):
    
    df_ranking_county = df_ranking_cv[df_ranking_cv.GEOID==fips_county]
    df_county_measures = df_all_counties[df_all_counties.GEOID==fips_county]

    custom_color_scale = {
        'Disability': '#673AB7',  
        'Health Outcomes': '#FFA726',  
        'Health Risk Behaviors': '#FFEB3B',  
        'Health Status': '#D32F2F',  
        'Prevention': '#4CAF50'  
    }
    categories = df_county_measures['Category'].unique()
    color_scale = {category: custom_color_scale.get(category, '#000000') for category in categories}  # Default to black if not found

    sorted_df = df_county_measures.sort_values(by='absolute_contribution', ascending=False)

    # Group by 'Category' and sum the 'percent_contribution'
    grouped_df = df_county_measures.groupby('Category')['absolute_contribution'].sum().reset_index()

    # Sort the grouped DataFrame by 'percent_contribution' in ascending order
    sorted_grouped_df = grouped_df.sort_values(by='absolute_contribution', ascending=False)
    # sorted_categories = sorted_grouped_df['Category'].tolist()

    fixed_order = [
        'Health Outcomes',
        'Disability', 
        'Prevention',
        'Health Status',
        'Health Risk Behaviors',
    ]
    # Ensure all categories from the data are included in the fixed order
    sorted_categories = [cat for cat in fixed_order if cat in categories]

    sorted_df['Category'] = pd.Categorical(sorted_df['Category'], categories=sorted_categories, ordered=True)
    sorted_df = sorted_df.sort_values(by=['Category', 'Data_Value'], ascending=[True, True])
    total = df_ranking_county['Weighted_Score_Normalized'].iloc[0].round(2)

    ###################################

    fig = make_subplots(rows=1, cols=2, column_widths=[0.75, 0.25], 
                        subplot_titles=('CDC PLACES<br>Health Survey Results',
                                        f"Contribution by Category<br>UnHealth Score Total: {total}"),
                                        )
    fig.update_yaxes(domain=[0.02, 0.98], row=1, col=1)  # Adjust domains as needed
    fig.update_yaxes(domain=[0.02, 0.98], row=1, col=2)
    # Map 'Category' to colors for the first chart
    colors_mapped = sorted_df['Category'].map(color_scale).tolist()

    # Add the first chart to the first column
    fig.add_trace(go.Bar(x=sorted_df['Data_Value'], y=sorted_df['Measure_short'],
                        orientation='h', marker_color=colors_mapped,
                        hovertemplate='%{y}: %{x:.2f}%<br>Contribution to UnHealth Score: %{customdata[1]:.2f}',
                        customdata=sorted_df[['Data_Value','absolute_contribution']],
                        name=''),
                row=1, col=1)

    for category in sorted_categories:
        df_filtered = sorted_grouped_df[sorted_grouped_df['Category'] == category]
        fig.add_trace(go.Bar(y=df_filtered['absolute_contribution'], x=[1]*len(df_filtered),
                            name=category, marker_color=color_scale[category],
                            text=category, orientation='v',
                            hovertemplate='Total category contribution: %{y:.2f}'),  
                    row=1, col=2)


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
    fig.update_yaxes(title_text="UnHealth Score", range=[0, total],
                     row=1, col=2)

    fig.update_traces(textposition='inside', textangle=0, insidetextanchor='middle', 
                    textfont=dict(size=18), selector=dict(orientation='v'))

    return fig



##############
# County map
percentile_high = df_ranking_cv['Weighted_Score_Normalized'].quantile(0.95)
percentile_low = df_ranking_cv['Weighted_Score_Normalized'].quantile(0.05)
num_counties = len(df_ranking_cv)

def create_county_map(selected_state, selected_county, df_ranking_cv,counties):
    
    # Filter the dataframe based on selected_state and selected_county
    
    filtered_df = df_ranking_cv[(df_ranking_cv['StateDesc'] == selected_state) & (df_ranking_cv['LocationName'] == selected_county)]

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
        #title_text='UnHealth Score for ' + selected_county + ', ' + selected_state,
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

