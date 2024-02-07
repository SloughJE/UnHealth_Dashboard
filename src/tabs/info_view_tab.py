import dash
import dash_bootstrap_components as dbc
from dash import html
from src.tabs.info_view import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

main_section_style = {
    'font-size': '2.5rem',  
    'background-color': '#C06070',  
    'color': 'white',  
}

sub_section_style = {
    'font-size': '2rem', 
    'background-color': '#F08080',  
    'color': 'white',  
}

# Function to create a collapsible card
def create_collapsible_card(header_id, collapse_id, title, content, header_style=sub_section_style, is_main=False):
    if is_main:
        button = dbc.Button(title, color="link", className="text-left", id=header_id, style={'font-size': '2.5rem', 'color': 'white'})
    else:
        button = dbc.Button(title, color="link", className="text-left", id=header_id, style={'font-size': '2rem', 'color': 'white'})
    
    card = dbc.Card([
        dbc.CardHeader(button, style=header_style),
        dbc.Collapse(
            dbc.CardBody(content),
            id=collapse_id,
        )
    ], className="mb-4")
    
    return card

def info_view_tab_layout():
    
    layout = dbc.Container([
        
        # Dashboard Information Section with Enhanced "UnHealth Score" Highlight
        create_collapsible_card("collapse-button-dashboard-info", "collapse-dashboard-info", dashboard_info_title, [
            html.P([
                "The aim of this Dashboard is to provide comprehensive insights into the health status of U.S. counties by integrating data from various government sources, including CDC health metrics, BEA economic data, BLS CPI data, and Census geolocation data. The focus is on the health measures provided by the CDC PLACES program. "
                "A key feature of our dashboard is the ",
                html.Strong("UnHealth Score™", style={'color': '#FF6347', 'fontSize': '16px'}),  
                ", a summary statistic designed to offer an in-depth assessment of county-level health. This score aggregates data from multiple health indicators, including chronic disease prevalence, lifestyle choices, and disability rates, facilitating direct comparisons between counties.\
                    The UnHealth Score™ highlights regions in urgent need of health interventions and support, serving as a critical tool for public health analysis and decision-making. Economic data is not factored into the UnHealth score."
                "\nThe UnHealth Dashboard consists of 3 main tabs, Summary View, County View and Measure View, described in the next section."
            ], style={'white-space': 'pre-line'}),
            html.H5(f"Developed by {developed_by}", style={'fontSize': '18px'}),
            html.Div([
                html.A("Dashboard GitHub Repo", href="https://github.com/SloughJE/UnHealth_Dashboard", target="_blank", style={'fontSize': '18px'})  
            ], style={'marginTop': '10px'}),
        ], header_style=main_section_style, is_main=True),
        
        # Tab Information Section
        create_collapsible_card("collapse-button-tab-info", "collapse-tab-info", tab_information_title, [
            create_collapsible_card("collapse-button-summary-view", "collapse-summary-view", summary_view_tab_title, [
                html.P(summary_view_tab_data, style={'white-space': 'pre-line'}),
                html.H5("GAM Model"),
                html.P(gam_model_description, style={'white-space': 'pre-line'}),
            ]),
            create_collapsible_card("collapse-button-county-view", "collapse-county-view", county_view_tab_title, [
                html.P(county_view_tab_data, style={'white-space': 'pre-line'}),
                html.P(county_view_key_features, style={'white-space': 'pre-line'}),
            ]),
            create_collapsible_card("collapse-button-measure-view", "collapse-measure-view", measure_view_tab_title, [
                html.P(measure_view_tab_data, style={'white-space': 'pre-line'}),
                html.P(measure_view_interactive_map, style={'white-space': 'pre-line'}),
                html.P(measure_selection_functionality, style={'white-space': 'pre-line'}),
                html.P(state_filtering_functionality, style={'white-space': 'pre-line'}),
                html.P(color_coding, style={'white-space': 'pre-line'}),
                html.P(best_worst_scores_table, style={'white-space': 'pre-line'}),
            ]),
        ], header_style=main_section_style, is_main=True),

        # Data Sources Section
        create_collapsible_card("collapse-button-data-sources", "collapse-data-sources", data_sources_title, [
            create_collapsible_card("collapse-button-cdc-places", "collapse-cdc-places", cdc_places_title, [
                html.P(cdc_places_data, style={'white-space': 'pre-line'}),
                html.A("CDC PLACES Program", href="https://www.cdc.gov/places/index.html", target="_blank"),
            ]),
            create_collapsible_card("collapse-button-bea", "collapse-bea", bea_title, [
                html.P(bea_data, style={'white-space': 'pre-line'}),
                html.A("Bureau of Economic Analysis", href="https://apps.bea.gov/regional/downloadzip.cfm", target="_blank"),
            ]),
            create_collapsible_card("collapse-button-census", "collapse-census", census_title, [
                html.P(census_data, style={'white-space': 'pre-line'}),
                html.A("US Census Bureau Geolocation Data", href="https://www2.census.gov/geo/tiger", target="_blank"),
            ]),
            create_collapsible_card("collapse-button-bls", "collapse-bls", bls_title, [
                html.P(bls_data, style={'white-space': 'pre-line'}),
                html.A("Bureau of Labor Statistics CPI", href="https://www.bls.gov/cpi/regional-resources.htm", target="_blank"),
            ]),
        ], header_style=main_section_style, is_main=True),
        
            create_collapsible_card("collapse-button-data-loading", "collapse-data-loading", data_loading_processing_title, [
                # CDC PLACES 
                create_collapsible_card("collapse-button-cdc-places-loading", "collapse-cdc-places-loading", cdc_places_loading_title, [
                    html.P(cdc_places_loading_data, style={'white-space': 'pre-line'}),
                    html.H4(unhealth_score_processing_title, className="mt-4"),  # Non-collapsible subsection header
                    html.P(unhealth_score_processing_data, style={'white-space': 'pre-line'}),  # Non-collapsible subsection content
                    html.H4(data_transformation_title, className="mt-4"),  # Another non-collapsible subsection header
                    html.P(data_transformation_data, style={'white-space': 'pre-line'}),  # Another non-collapsible subsection content
                ], header_style=sub_section_style),
                # BEA GDP and Income Data
                create_collapsible_card("collapse-button-bea-gdp-income", "collapse-bea-gdp-income", bea_gdp_income_title, [
                    html.H5(gdp_loading_title, className="mt-3"),
                    html.P(gdp_loading_data, style={'white-space': 'pre-line'}),
                    html.H5(income_loading_title, className="mt-3"),
                    html.P(income_loading_data, style={'white-space': 'pre-line'}),
                ], header_style=sub_section_style),
                
                # BLS CPI Data
                create_collapsible_card("collapse-button-bls-cpi", "collapse-bls-cpi", bls_cpi_title, [
                    html.H5(regional_cpi_title, className="mt-3"),
                    html.P(regional_cpi_data, style={'white-space': 'pre-line'}),
                    html.H5(usa_cpi_title, className="mt-3"),
                    html.P(usa_cpi_data, style={'white-space': 'pre-line'}),
                ], header_style=sub_section_style),
                # BEA and BLS Data Further Processing
                create_collapsible_card("collapse-button-bea-bls-further-processing", "collapse-bea-bls-further-processing", bea_bls_further_processing_title, [
                    html.P(bea_bls_further_processing_text, style={'white-space': 'pre-line'}),
                ], header_style=sub_section_style),

            ], header_style=main_section_style, is_main=True),



        ], fluid=True, style={'marginTop':'20px'})
    return layout

