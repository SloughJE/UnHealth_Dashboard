import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Your existing functions
from src.tabs.county_view import (create_county_econ_charts, create_county_health_charts, create_county_map, 
                                df_all_counties, df_ranking, df_bea, counties
                                )

def create_kpi_layout(df_ranking, fips_county):

    selected_data = df_ranking[df_ranking.GEOID==fips_county].iloc[0]
    health_metric = selected_data['Weighted_Score_Normalized']
    rank = selected_data['Rank']

    return html.Div([
        html.H3(f"County Health Metric: {health_metric:.2f}", style={'color': 'white'}),
        html.H3(f"Rank: {rank}", style={'color': 'white'})
    ])


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
        # Dropdown for State
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in df_ranking['StateAbbr'].unique()],
            placeholder="Select a State"
        ),

        # Dropdown for County, updated based on State
        dcc.Dropdown(
            id='county-dropdown',
            placeholder="Select a County"
        ),
            # Button to show data
            html.Button('Show County Data', id='show-data-button')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            # KPIs here
            html.Div(id='kpi-display')
        ], width=6),
        dbc.Col([
            # County map
            dcc.Graph(id='county-map')
        ], width=6)
    ]),
    dbc.Row([
        # Health metric chart
        dcc.Graph(id='county-health-chart',
            style={'height': '700px'})
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

    # Layout for Economic Charts
    dbc.Row([
        # Column for the first economic chart
        dbc.Col(
            dcc.Graph(id='econ-chart-1'), 
            width=6  # This specifies that the column takes up half of the row
        ),
        # Column for the second economic chart
        dbc.Col(
            dcc.Graph(id='econ-chart-2'), 
            width=6  # Similarly, this takes up the other half of the row
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
        counties = df_ranking[df_ranking['StateAbbr'] == selected_state]['LocationName'].unique()
        return [{'label': county, 'value': county} for county in counties]
    return []


@app.callback(
    [
        Output('kpi-display', 'children'),
        Output('county-map', 'figure'),
        Output('county-health-chart', 'figure'),
        Output('econ-chart-1', 'figure'),  # Updated output
        Output('econ-chart-2', 'figure')   # Updated output
    ],
    [
        Input('show-data-button', 'n_clicks'),
        Input('currency-type', 'value')  # New input
    ],
    [State('state-dropdown', 'value'), State('county-dropdown', 'value')]
)
def update_charts(n_clicks, currency_type, selected_state, selected_county):
    if n_clicks is None:
        return dash.no_update

    fips_county = df_ranking[(df_ranking.StateAbbr == selected_state) & (df_ranking.LocationName == selected_county)].GEOID.iloc[0]
    
    kpi_layout = create_kpi_layout(df_ranking, fips_county) 
    county_map_figure = create_county_map(selected_state, selected_county, df_ranking, counties)
    county_health_figure = create_county_health_charts(df_ranking, df_all_counties, fips_county)
    
    fig_adj_income, fig_income, fig_real_gdp, fig_gdp = create_county_econ_charts(df_bea, fips_county)
    
    if currency_type == 'adj':
        return kpi_layout, county_map_figure, county_health_figure, fig_adj_income, fig_real_gdp
    else:
        return kpi_layout, county_map_figure, county_health_figure, fig_income, fig_gdp


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)