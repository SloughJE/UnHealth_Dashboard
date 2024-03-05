import dash
from dash import html
import dash_bootstrap_components as dbc

from src.tabs.helper_data import unhealth_score_explanation
from src.tabs.ai_patient_view import create_updated_ai_patient_view

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

