import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Your existing functions
from src.tabs.county_view import (
                                create_county_econ_charts, create_county_health_charts, create_county_map, 
                                calculate_percent_difference_econ,check_fips_county_data,
                                df_all_counties, df_ranking, df_bea, counties
                                )
# Define the common style
common_div_style = {
    'backgroundColor': 'black', 
    'padding': '10px', 
    'border-radius': '5px',
    'margin-bottom': '20px'  # Optional, adds space between components
}

def create_kpi_layout(df_ranking, fips_county, df_bea_county, fips_county_bea):

    # Get the corresponding GeoName for fips_county_bea
    geo_name_bea = df_bea[df_bea.GeoFips == fips_county_bea].GeoName.iloc[0] if not df_bea[df_bea.GeoFips == fips_county_bea].empty else "Unknown"
    # Check if fips_county and fips_county_bea are different
    if fips_county != fips_county_bea:
        note = html.P(f"Note: Economic data displayed is based on {geo_name_bea} (FIPS: {fips_county_bea}) due to data availability.", style={'color': 'yellow'})
    else:
        note = html.P()

    selected_data = df_ranking[df_ranking.GEOID==fips_county].iloc[0]
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

    # KPI Layout with black background
    kpi_layout = html.Div([
        html.H2(f"{county_name}, {state_name}", style={'color': 'white', 'margin-bottom': '20px'}),
        html.Div([
            html.H3(f"Health Score: {health_metric:.2f} (out of 100)", style={'color': 'white'}),
            html.H3(f"Rank: {rank} of {len(df_ranking)}", style={'color': 'white'}),
        ], style={'margin-bottom': '20px'}),
        html.Div([
            html.H3(gdp_percent_text, style={'color': 'white'}),
            html.H3(income_percent_text, style={'color': 'white'}),
        ], style={'margin-bottom': '20px'}),
        html.H3(f"Population ({year_bea}): {pop_county_formatted}", style={'color': 'white'}),
        note
    ])

    return kpi_layout


default_state = 'AK'  
default_county = 'Aleutians East'


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
# Custom CSS to reset default browser styles
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})



# App layout
app.layout = dbc.Container([
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0,
        max_intervals=1  # Ensure it triggers only once
    ),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df_ranking['StateAbbr'].unique())],
                value=default_state,  # Set default value
                placeholder="Select a State",
            ),
            dcc.Dropdown(
                id='county-dropdown',
                value=default_county,  # Set default value
                placeholder="Select a County"
            ),
            html.Button('Show County Data', id='show-data-button')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='kpi-display', style={**common_div_style,'height': '95%'}), width=6),
        dbc.Col(html.Div(dcc.Graph(id='county-map'), style={**common_div_style, 'height': '95%'}), width=6)
    ], align="stretch"),  # Setting align to "stretch" for equal height columns
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(id='county-health-chart', style={'height': '800px'}),
                style=common_div_style
            ),
            width=12  # Use the full width of the row
        )
    ]),
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id='currency-type',
                options=[
                    {'label': 'Adjusted Dollars', 'value': 'adj'},
                    {'label': 'Current Dollars', 'value': 'current'}
                ],
                value='adj',  # Default value
                labelStyle={'display': 'inline-block', 'margin-right': '20px'},
                style={'text-align': 'center', 'color': 'white'}
            )
        ], width=12)
    ]),
    dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(id='econ-chart-1'), style=common_div_style), 
                width=6
            ),
            dbc.Col(
                html.Div(dcc.Graph(id='econ-chart-2'), style=common_div_style), 
                width=6
            )
        ]),
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(id='econ-pop'), 
                style=common_div_style
            ),
            width=12  # Use the full width of the row
        )
    ]),
], fluid=True)

# Callback to update county dropdown based on state selection
@app.callback(
    Output('county-dropdown', 'options'),
    [Input('state-dropdown', 'value')]
)
def update_county_dropdown(selected_state):
    if selected_state is not None:
        counties = sorted(df_ranking[df_ranking['StateAbbr'] == selected_state]['LocationName'].unique())
        return [{'label': county, 'value': county} for county in counties]
    return []


@app.callback(
    [
        Output('kpi-display', 'children'),
        Output('county-map', 'figure'),
        Output('county-health-chart', 'figure'),
        Output('econ-chart-1', 'figure'), 
        Output('econ-chart-2', 'figure'),
        Output('econ-pop', 'figure')  
    ],
    [
        Input('interval-component', 'n_intervals'),
        Input('show-data-button', 'n_clicks'),
        Input('currency-type', 'value')
    ],
    [State('state-dropdown', 'value'), State('county-dropdown', 'value')]
)
def update_charts(n_intervals, n_clicks, currency_type, selected_state, selected_county):
    if n_intervals == 0 and n_clicks is None:
        return dash.no_update

    # Ensure selected_state and selected_county have values
    selected_state = selected_state or default_state
    selected_county = selected_county or default_county
    
    fips_county = df_ranking[(df_ranking.StateAbbr == selected_state) & (df_ranking.LocationName == selected_county)].GEOID.iloc[0]
    fips_county_bea = check_fips_county_data(df_bea,fips_county,selected_state, selected_county)
    # fips_usa = 00000
    df_bea_county = df_bea[(df_bea.GeoFips=="00000") | (df_bea.GeoFips==fips_county_bea)]

    kpi_layout = create_kpi_layout(df_ranking, fips_county, df_bea_county, fips_county_bea) 
    county_map_figure = create_county_map(selected_state, selected_county, df_ranking, counties)
    county_health_figure = create_county_health_charts(df_ranking, df_all_counties, fips_county)
    
    fig_adj_income, fig_income, fig_real_gdp, fig_gdp, fig_pop= create_county_econ_charts(df_bea_county)
    
    if currency_type == 'adj':
        return kpi_layout, county_map_figure, county_health_figure, fig_adj_income, fig_real_gdp, fig_pop
    else:
        return kpi_layout, county_map_figure, county_health_figure, fig_income, fig_gdp, fig_pop


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)