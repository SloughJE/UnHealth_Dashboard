import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from src.tabs.county_view import (
                                create_county_econ_charts, create_county_health_charts, create_county_map, 
                                calculate_percent_difference_econ,check_fips_county_data,
                                df_all_counties, df_ranking, df_bea, counties, health_score_explanation
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
        
    info_icon = html.I(className="bi bi-info-circle", id="health-score-tooltip-target", style={'cursor': 'pointer','font-size': '22px'})
    health_score_with_icon = html.H3(
        ["Health Score ", info_icon],
        style={'color': 'white'}
    )
    health_score_tooltip = dbc.Tooltip(
        health_score_explanation,
        target="health-score-tooltip-target",
        placement="right",
        className='custom-tooltip'
    )
    kpi_layout = html.Div([
        #html.H2(f"{county_name}, {state_name}", style={'color': 'white','text-align': 'center'}),
        html.Div([
            health_score_with_icon,
            html.P(f"{health_metric:.2f} (out of 100)", style={'color': 'white', 'font-size': '1.2em'}),
            #html.Small("Note: Higher scores indicate worse health outcomes.", style={'color': 'yellow', 'font-size': '0.8em'}),  # Explanatory note
            html.H3("Rank", style={'color': 'white'}),
            html.P(f"{rank} of {len(df_ranking)}", style={'color': 'white', 'font-size': '1.2em'}),
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


default_state = 'Alaska'  
default_county = 'Kusilvak'


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dcc.Interval(
        id='interval-component',
        interval=500,  # in milliseconds
        n_intervals=0,
        max_intervals=1  # Ensure it triggers only once
    ),
    html.H1("County View", style={'text-align': 'center', 'margin-top': '20px','margin-bottom': '20px','font-size':'5em'}),
    html.P("Please select a state and county from the dropdowns below and press the button to view county data.", style={'text-align': 'left'}),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df_ranking['StateDesc'].unique())],
                value=default_state,  # Set default value
                placeholder="Select a State",
                style={'margin-bottom': '10px','font-size': '1.2em'}
            ),
            dcc.Dropdown(
                id='county-dropdown',
                value=default_county,  # Set default value
                placeholder="Select a County",
                style={'margin-bottom': '10px','font-size': '1.2em'}
            ),
            html.Button(
                'Show County Data', 
                id='show-data-button', 
                className='button-top-margin custom-button'
            )
        ], width=6)
    ]),

    html.Div(id='selected-title', style={'text-align': 'center', 'font-size': '3.5em', 'margin-bottom': '0px'}),  # Placeholder for the dynamic title
    
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
    dbc.Row(
        dbc.Col([
            html.H4("Monetary Basis:", className='monetary-basis-heading'),
            dcc.RadioItems(
                id='currency-type',
                options=[
                    {'label': 'Adjusted Dollars (CPI)', 'value': 'adj'},
                    {'label': 'Current Dollars', 'value': 'current'}
                ],
                value='adj',  # Default value
                className='radio-button-style',
                inputStyle={"margin-right": "5px"},
                labelStyle={"display": "inline-block", "margin-right": "20px"},  # Make labels inline
                style={'text-align': 'center'}
            ),
            html.P("Select the basis for dollar values displayed in the charts below.", className='radio-button-instruction')
        ], width=12, className='text-center'),
        justify="center"
    ),
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
        counties = sorted(df_ranking[df_ranking['StateDesc'] == selected_state]['LocationName'].unique())
        return [{'label': county, 'value': county} for county in counties]
    return []


@app.callback(
    [
        Output('selected-title', 'children'),
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
    
    fips_county = df_ranking[(df_ranking.StateDesc == selected_state) & (df_ranking.LocationName == selected_county)].GEOID.iloc[0]
    fips_county_bea = check_fips_county_data(df_bea,fips_county,selected_state, selected_county)
    # fips_usa = 00000
    df_bea_county = df_bea[(df_bea.GeoFips=="00000") | (df_bea.GeoFips==fips_county_bea)]
    county_map_figure = create_county_map(selected_state, selected_county, df_ranking, counties)

    kpi_layout = create_kpi_layout(df_ranking, fips_county, df_bea_county, fips_county_bea) 
    county_health_figure = create_county_health_charts(df_ranking, df_all_counties, fips_county)
    
    fig_adj_income, fig_income, fig_real_gdp, fig_gdp, fig_pop= create_county_econ_charts(df_bea_county)
    
    dynamic_title = f"{selected_county}, {selected_state}"  # Format the title

    if currency_type == 'adj':
        return dynamic_title, kpi_layout, county_map_figure, county_health_figure, fig_adj_income, fig_real_gdp, fig_pop
    else:
        return dynamic_title, kpi_layout, county_map_figure, county_health_figure, fig_income, fig_gdp, fig_pop


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)