import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from src.tabs.county_view import df_ranking_cv
from src.tabs.helper_data import common_div_style, unhealth_score_explanation
from src.tabs.ai_patient_view import (create_updated_ai_patient_view, all_patient_ids)

default_patient_id = "e154f937-18c5-ebaa-1fd0-0b714169d18b"  

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])

def ai_patient_view_tab_layout():
    
    default_layout = create_updated_ai_patient_view(default_patient_id)

    layout = dbc.Container([
        html.Div([
            html.Button('Generate Random Patient Data', id='generate-random-patient-button', className='custom-button-ai'),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'}),
        html.Div(id='ai-patient-view-content', children=default_layout)
    ], fluid=True, style={'marginTop': '20px'})    
    
    
    return layout

