import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from src.tabs.county_view import (
                                create_county_econ_charts, create_county_health_charts, create_county_map, 
                                check_fips_county_data, create_kpi_layout,
                                df_all_counties, df_ranking_cv, df_bea, counties
                                )

from src.tabs.helper_data import common_div_style, centered_div_style, health_score_explanation

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
    
    html.Div([
        html.Div("Please select a state and county from the dropdowns below and press the button to view county data.", style={'textAlign': 'center'}),
        
        html.Div([
            dbc.Col([
                dcc.Dropdown(
                    id='state-dropdown',
                    options=[{'label': state, 'value': state} for state in sorted(df_ranking_cv['StateDesc'].unique())],
                    value=default_state,  # Set default value
                    placeholder="Select a State",
                    style={'marginBottom': '10px', 'fontSize': '1.2em', 'width': '400px','marginTop': '10px'}
                ),
                dcc.Dropdown(
                    id='county-dropdown',
                    value=default_county,  # Set default value
                    placeholder="Select a County",
                    style={'marginBottom': '10px', 'fontSize': '1.2em', 'width': '400px'}
                ),
                html.Div([
                html.Button(
                    'Show County Data', 
                    id='show-data-button', 
                    className='custom-button'
                )
            ], style={'display': 'flex', 'justifyContent': 'center'})  # Center-align the button
        ], width=12)
        ])  # Apply common_div_style to the wrapping Div
    ], style={**common_div_style, **centered_div_style, 'width':'50%','marginLeft': 'auto','marginRight': 'auto'}),

    html.Div(id='selected-title', style={'text-align': 'center', 'font-size': '3.5em', 'margin-bottom': '0px', 'margin': '0 auto'}),  
    
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
        counties = sorted(df_ranking_cv[df_ranking_cv['StateDesc'] == selected_state]['LocationName'].unique())
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
    
    fips_county = df_ranking_cv[(df_ranking_cv.StateDesc == selected_state) & (df_ranking_cv.LocationName == selected_county)].GEOID.iloc[0]
    fips_county_bea = check_fips_county_data(df_bea,fips_county,selected_state, selected_county)
    # fips_usa = 00000
    df_bea_county = df_bea[(df_bea.GeoFips=="00000") | (df_bea.GeoFips==fips_county_bea)]
    county_map_figure = create_county_map(selected_state, selected_county, df_ranking_cv, counties)

    kpi_layout = create_kpi_layout(df_ranking_cv, fips_county, df_bea_county, fips_county_bea, health_score_explanation) 
    county_health_figure = create_county_health_charts(df_ranking_cv, df_all_counties, fips_county)
    
    fig_adj_income, fig_income, fig_real_gdp, fig_gdp, fig_pop= create_county_econ_charts(df_bea_county)
    
    dynamic_title = f"{selected_county}, {selected_state}"  # Format the title

    if currency_type == 'adj':
        return dynamic_title, kpi_layout, county_map_figure, county_health_figure, fig_adj_income, fig_real_gdp, fig_pop
    else:
        return dynamic_title, kpi_layout, county_map_figure, county_health_figure, fig_income, fig_gdp, fig_pop


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)