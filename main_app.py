import dash
import random

from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from src.tabs.overall_view_tab import overall_view_tab_layout
from src.tabs.county_view_tab import county_view_tab_layout,default_state, default_county
from src.tabs.measure_view_tab import measure_view_tab_layout
from src.tabs.info_view_tab import info_view_tab_layout
from src.tabs.ai_patient_view_tab import ai_patient_view_tab_layout, all_patient_ids, create_updated_ai_patient_view

from src.tabs.overall_view import (create_updated_map, create_updated_scatter_chart, find_top_bottom_values, value_to_color,
                                   df_ranking, x_pred, y_pred, y_intervals, percentile_low, percentile_high, pseudo_r2_value)

from src.tabs.county_view import (
                                create_county_econ_charts, create_county_health_charts, create_county_map, 
                                create_kpi_layout,
                                df_all_counties, df_ranking_cv, df_bea, counties, 
                                )
from src.tabs.measure_view import (create_updated_map_measures,find_top_bottom_values, value_to_color,
    df_measures, 
)
from src.tabs.info_view import *

from src.tabs.helper_data import unhealth_score_explanation


# Initialize the main Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])
server = app.server # Expose the Flask server for Gunicorn

# Main app layout
app.layout = dbc.Container([

    html.H1("The UnHealth™ Dashboard", style={
        'color': 'white',
        'font-size':'3vw',
        'textAlign': 'center',
        'margin-top': '20px',
        #'position': 'sticky',
        #'top': '0',
        #'zIndex': '1000',
        #'backgroundColor': '#333',
        }),

    dcc.Tabs(id="tabs", value='tab-1', className='tab-container', children=[
        dcc.Tab(label='Summary View', value='tab-1', className='custom-tab', selected_className='custom-tab-active', children=overall_view_tab_layout()),
        dcc.Tab(label='County View', value='tab-2', className='custom-tab', selected_className='custom-tab-active', children=county_view_tab_layout()),
        dcc.Tab(label='Measure View', value='tab-3', className='custom-tab', selected_className='custom-tab-active',children=measure_view_tab_layout()),
        dcc.Tab(label='AI Patient View', value='tab-4', className='custom-tab', selected_className='custom-tab-active',children=ai_patient_view_tab_layout()),
        dcc.Tab(label='Info', value='tab-5', className='custom-tab', selected_className='custom-tab-active',children=info_view_tab_layout()),
    ], style={'position': 'sticky', 'top': '0', 'zIndex': '1000'}),
        
    
    html.Div(id='tabs-content')
    ], fluid=True)


##################
###OVERALL VIEW###
##################

# Define callback to update map and chart based on user input
@app.callback(
    [Output('choropleth-map', 'figure'), Output('scatter-chart', 'figure')],
    [Input('state-dropdown', 'value')]
)
def update_map_and_chart(selected_state):

    # Create and return the updated figures for map and scatter chart
    updated_map_fig = create_updated_map(df_ranking, selected_state)
    updated_scatter_chart_fig = create_updated_scatter_chart(df_ranking, selected_state,x_pred, y_pred, y_intervals,pseudo_r2_value)

    return updated_map_fig, updated_scatter_chart_fig

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
    fips_county, fips_county_bea = df_ranking_cv.loc[(df_ranking_cv.StateDesc == selected_state) & \
                                                     (df_ranking_cv.LocationName == selected_county), ['GEOID', 'matched_GEOID']].iloc[0]

    # fips_usa = 00000
    df_bea_county = df_bea[(df_bea.GeoFips=="00000") | (df_bea.GeoFips==fips_county_bea)]
    county_map_figure = create_county_map(selected_state, selected_county, df_ranking_cv, counties)

    kpi_layout = create_kpi_layout(df_ranking_cv, fips_county, df_bea_county, fips_county_bea, unhealth_score_explanation) 
    county_health_figure = create_county_health_charts(df_ranking_cv, df_all_counties, fips_county)
    
    fig_adj_income, fig_income, fig_real_gdp, fig_gdp, fig_pop= create_county_econ_charts(df_bea_county)
    
    dynamic_title = f"{selected_county}, {selected_state}"  

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

    # Create and return the updated figures for map and scatter chart
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

@app.callback(
    Output('measure-subtitle', 'children'),
    [Input('measure-dropdown', 'value')]
)
def update_measure_subtitle(selected_measure):
 
    return selected_measure


##############################
######AI PATIENT VIEW TAB#####
##############################

# Callback to generate and display random patient data
@app.callback(
    Output('ai-patient-view-content', 'children'),
    [Input('generate-random-patient-button', 'n_clicks')],
    prevent_initial_call=False  # Prevent callback from running on app initialization
)

def display_random_patient_data(n_clicks):
    
    if n_clicks is None:
        random_patient_id = "e154f937-18c5-ebaa-1fd0-0b714169d18b"
        patient_id_title, summary_card, vital_signs_card, labs_card, qols_card = create_updated_ai_patient_view(random_patient_id)  

        return summary_card, vital_signs_card, labs_card, qols_card
    
    random_patient_id = random.choice(all_patient_ids)  
    patient_id_title, summary_card, vital_signs_card, labs_card, qols_card = create_updated_ai_patient_view(random_patient_id)  

    return patient_id_title, summary_card, vital_signs_card, labs_card, qols_card


@app.callback(
    Output("collapse-summary", "is_open"),
    [Input("collapse-summary-header", "n_clicks")],
    [State("collapse-summary", "is_open")],
)
def toggle_summary_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-charts", "is_open"),
    [Input("collapse-charts-header", "n_clicks")],
    [State("collapse-charts", "is_open")]
)
def toggle_charts_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-vital-signs", "is_open"),
    [Input("collapse-vital-signs-header", "n_clicks")],
    [State("collapse-vital-signs", "is_open")]
)
def toggle_vital_signs_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-qols", "is_open"),
    [Input("collapse-qols-header", "n_clicks")],
    [State("collapse-qols", "is_open")]
)
def toggle_qols_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


#######################
######INFO TAB#########
#######################

# Callbacks for toggling the collapse

toggle_callbacks = [
    {"trigger": "collapse-button-dashboard-info", "target": "collapse-dashboard-info"},
    {"trigger": "collapse-button-tab-info", "target": "collapse-tab-info"},
    {"trigger": "collapse-button-summary-view", "target": "collapse-summary-view"},
    {"trigger": "collapse-button-county-view", "target": "collapse-county-view"},
    {"trigger": "collapse-button-measure-view", "target": "collapse-measure-view"},
    {"trigger": "collapse-button-data-sources", "target": "collapse-data-sources"},
    {"trigger": "collapse-button-cdc-places", "target": "collapse-cdc-places"},
    {"trigger": "collapse-button-bea", "target": "collapse-bea"},
    {"trigger": "collapse-button-census", "target": "collapse-census"},
    {"trigger": "collapse-button-bls", "target": "collapse-bls"},
    {"trigger": "collapse-button-data-loading", "target": "collapse-data-loading"},
    {"trigger": "collapse-button-cdc-places-loading", "target": "collapse-cdc-places-loading"},
    {"trigger": "collapse-button-bea-gdp-income", "target": "collapse-bea-gdp-income"},
    {"trigger": "collapse-button-bls-cpi", "target": "collapse-bls-cpi"},
    {"trigger": "collapse-button-bea-bls-further-processing", "target": "collapse-bea-bls-further-processing"},

]

for callback in toggle_callbacks:
    @app.callback(
        Output(callback["target"], "is_open"),
        [Input(callback["trigger"], "n_clicks")],
        [State(callback["target"], "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)