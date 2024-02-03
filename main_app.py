import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from src.tabs.overall_view_tab import overall_view_tab_layout
from src.tabs.county_view_tab import county_view_tab_layout,default_state, default_county
from src.tabs.measure_view_tab import measure_view_tab_layout

from src.tabs.overall_view import (create_updated_map, create_updated_bubble_chart, find_top_bottom_values, value_to_color,
                                   df_ranking, df_gam, x_pred, y_pred, y_intervals, percentile_low, percentile_high, pseudo_r2_value)

from src.tabs.county_view import (
                                create_county_econ_charts, create_county_health_charts, create_county_map, 
                                check_fips_county_data, create_kpi_layout,
                                df_all_counties, df_ranking_cv, df_bea, counties, 
                                )
from src.tabs.measure_view import (create_updated_map_measures,find_top_bottom_values, value_to_color,
    df_measures, 
)
from src.tabs.helper_data import health_score_explanation


# Initialize the main Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

# Main app layout
app.layout = dbc.Container([
    html.H1("The UnHealth™ Dashboard", style={
        'color': 'white',
        'font-size':'5em',
        'textAlign': 'center',
        'margin-top': '20px',
    }),

    dcc.Tabs(id="tabs", value='tab-1', className='tab-container', children=[
        dcc.Tab(label='Summary View', value='tab-1', className='custom-tab', selected_className='custom-tab-active', children=overall_view_tab_layout()),
        dcc.Tab(label='County View', value='tab-2', className='custom-tab', selected_className='custom-tab-active', children=county_view_tab_layout()),
        dcc.Tab(label='Measure View', value='tab-3', className='custom-tab', selected_className='custom-tab-active',children=measure_view_tab_layout()),
        dcc.Tab(label='Help / Information', value='tab-4', className='custom-tab', selected_className='custom-tab-active'),
    ]),
        
        html.Div(id='tabs-content')
    ], fluid=True)


##################
###OVERALL VIEW###
##################

# Define callback to update map and chart based on user input
@app.callback(
    [Output('choropleth-map', 'figure'), Output('bubble-chart', 'figure')],
    [Input('state-dropdown', 'value')]
)
def update_map_and_chart(selected_state):

    # Create and return the updated figures for map and bubble chart
    updated_map_fig = create_updated_map(df_ranking, selected_state)
    updated_bubble_chart_fig = create_updated_bubble_chart(df_gam, selected_state,x_pred, y_pred, y_intervals,pseudo_r2_value)

    return updated_map_fig, updated_bubble_chart_fig

@app.callback(
    Output('state-data-table', 'data'),
    Output('state-data-table', 'style_data_conditional'),
    [Input('state-dropdown', 'value')]
)
def update_table(selected_state):
    max_values = 10  # Number of top and bottom values

    if selected_state:
        # Filter DataFrame based on selected state
        filtered_df = df_ranking[df_ranking['StateDesc'].isin(selected_state)]
    else:
        # If no state is selected, use the full dataset
        filtered_df = df_ranking
    # Get top and bottom values based on filtered DataFrame

    top_bottom_df = find_top_bottom_values(filtered_df, 'Weighted_Score_Normalized', max_values)
    # Calculate colors for each row in the top_bottom_df based on overall min and max values
    top_bottom_df['Color'] = top_bottom_df['Weighted_Score_Normalized'].apply(lambda x: value_to_color(x, percentile_low, percentile_high))
    top_bottom_df['Weighted_Score_Normalized'] = round(top_bottom_df.Weighted_Score_Normalized,2)

    top_bottom_df['Per capita personal income'] = round(top_bottom_df['Per capita personal income'],0)
    top_bottom_df.fillna("NA",inplace=True)

    # Convert DataFrame to dictionary for DataTable
    data = top_bottom_df.to_dict('records')

    # Define style conditions using the Color column
    style = [{'if': {'row_index': i}, 'backgroundColor': color} for i, color in enumerate(top_bottom_df['Color'])]

    # Additional style settings for borders and lines
    style.extend([
        {'if': {'column_id': 'LocationName'}, 'textAlign': 'left'},
        {'if': {'column_id': 'StateDesc'}, 'textAlign': 'left'}

    ])
    return data, style


#################
###County View###
#################

# Callback to update county dropdown based on state selection
@app.callback(
    Output('county-view-county-dropdown', 'options'),
    [Input('county-view-state-dropdown', 'value')]
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
    [State('county-view-state-dropdown', 'value'), State('county-view-county-dropdown', 'value')]
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


##################
###Measure View###
##################
    
# Define callback to update map and chart based on user input
@app.callback(
    Output('measure-view-choropleth-map', 'figure'),
    [Input('measure-dropdown', 'value'),
     Input('measure-view-state-dropdown', 'value')]
)
def update_map_and_chart(selected_measure, selected_state):

    # Create and return the updated figures for map and bubble chart
    updated_map_fig = create_updated_map_measures(df_measures, selected_state, selected_measure)

    return updated_map_fig

@app.callback(
    Output('measure-view-state-data-table', 'data'),
    Output('measure-view-state-data-table', 'style_data_conditional'),
    [Input('measure-dropdown', 'value'),
     Input('measure-view-state-dropdown', 'value')]
)
def update_table(selected_measure, selected_state):

    max_values = 10  # Number of top and bottom values
    df_measures_filtered = df_measures[(df_measures['Measure_short'] == selected_measure)]
    # Calculate the 10th and 90th percentiles of the data
    percentile_low = df_measures_filtered['Data_Value'].quantile(0.05)
    percentile_high = df_measures_filtered['Data_Value'].quantile(0.95)
    
    if selected_state:
        # Filter DataFrame based on selected state
        filtered_df = df_measures_filtered[df_measures_filtered['StateDesc'].isin(selected_state)]
    else:
        # If no state is selected, use the full dataset
        filtered_df = df_measures_filtered
    # Get top and bottom values based on filtered DataFrame

    top_bottom_df = find_top_bottom_values(filtered_df, 'Data_Value', max_values)
    # Calculate colors for each row in the top_bottom_df based on overall min and max values
    top_bottom_df['Color'] = top_bottom_df['Data_Value'].apply(lambda x: value_to_color(x, percentile_low, percentile_high))
    #top_bottom_df['Weighted_Score_Normalized'] = round(top_bottom_df.Weighted_Score_Normalized,2)

    #top_bottom_df['Per capita personal income'] = round(top_bottom_df['Per capita personal income'],0)
    #top_bottom_df.fillna("NA",inplace=True)

    # Convert DataFrame to dictionary for DataTable
    data = top_bottom_df.to_dict('records')

    # Define style conditions using the Color column
    style = [{'if': {'row_index': i}, 'backgroundColor': color} for i, color in enumerate(top_bottom_df['Color'])]

    # Additional style settings for borders and lines
    style.extend([
        {'if': {'column_id': 'LocationName'}, 'textAlign': 'left'},
        {'if': {'column_id': 'StateDesc'}, 'textAlign': 'left'}

    ])
    return data, style


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)