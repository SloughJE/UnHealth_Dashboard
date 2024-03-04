import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from src.tabs.county_view import df_ranking_cv
from src.tabs.helper_data import common_div_style, unhealth_score_explanation
from src.tabs.ai_patient_view import (create_collapsible_summary_card, 
                                      load_patient_summary, 
                                      create_collapsible_charts_card, 
                                      get_labs_for_single_patient, 
                                      create_charts_patient,
                                      create_vital_signs_charts,
                                      create_collapsible_vital_signs_card,
                                      create_qols_chart,
                                      create_collapsible_qols_card)

# load lab data
patient_labs_dir="data/processed/patient_labs/"
df_labs = pd.read_pickle(f"{patient_labs_dir}df_patient_labs.pkl")
df_vital_signs = pd.read_pickle(f"{patient_labs_dir}df_vital_signs.pkl")
df_qols_scores = pd.read_pickle(f"{patient_labs_dir}df_qols_scores.pkl")


def ai_patient_view_tab_layout(patient_id="e154f937-18c5-ebaa-1fd0-0b714169d18b"):
    patient_summary = load_patient_summary(patient_id)
    summary_card = create_collapsible_summary_card("AI Patient Summary", patient_summary)

    df_labs_patient, df_vital_signs_patient, df_qols_scores_patient = get_labs_for_single_patient(df_labs, df_vital_signs, df_qols_scores, patient_id)
    lab_figures = create_charts_patient(df_labs_patient)
    charts_card = create_collapsible_charts_card("Labs", lab_figures)

    vital_signs_figures = create_vital_signs_charts(df_vital_signs_patient)
    vital_signs_card = create_collapsible_vital_signs_card("Vitals", vital_signs_figures)

    qols_figure = create_qols_chart(df_qols_scores_patient)
    qols_card = create_collapsible_qols_card("Quality of Life Score", qols_figure)
    
    layout = dbc.Container([
        summary_card,
        charts_card,
        vital_signs_card,
        qols_card
    ], fluid=True, style={'marginTop': '20px'})
    
    return layout
