import json
import os

import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from src.tabs.helper_data import ai_summary_explanation

# load lab data
patient_labs_dir="data/processed/patient_labs/"
df_labs = pd.read_pickle(f"{patient_labs_dir}df_patient_filt_labs.pkl")
df_vital_signs = pd.read_pickle(f"{patient_labs_dir}df_vital_filt_signs.pkl")
df_qols_scores = pd.read_pickle(f"{patient_labs_dir}df_qols_filt_scores.pkl")

patient_ids_labs = df_labs['PATIENT'].unique().tolist()
patient_ids_vital_signs = df_vital_signs['PATIENT'].unique().tolist()
patient_ids_qols_scores = df_qols_scores['PATIENT'].unique().tolist()
all_patient_ids = list(set(patient_ids_labs + patient_ids_vital_signs + patient_ids_qols_scores))


directory_path = "data/processed/AI_summaries"
all_patient_ids = []
for filename in os.listdir(directory_path):
    if filename.endswith(".json"):
        patient_id = filename[:-5]  
        all_patient_ids.append(patient_id)


def load_patient_summary(patient_id):
    filename = f"data/processed/AI_summaries/{patient_id}.json"  
    with open(filename, 'r') as file:
        patient_summary = json.load(file)
    return patient_summary["summary"]

def create_collapsible_summary_card(title, content):
    header_id = "collapse-summary-header"
    collapse_id = "collapse-summary"
    info_icon_id = "info-icon"
    
    # Define the button with the title and an information icon
    button = html.Div([
        dbc.Button(
            title,
            color="link",
            className="text-left",
            id=header_id,
            style={'font-size': '2.5rem', 'color': 'white'},
        ),
        html.I(className="bi bi-info-circle", id=info_icon_id, style={'cursor': 'pointer', 'marginLeft': '0px', 'marginTop': '15px', 'fontSize': '22px'}),
    ], style={'display': 'flex', 'alignItems': 'center'})


    card = dbc.Card([
        dbc.CardHeader(button),
        dbc.Collapse(
            dbc.CardBody(dcc.Markdown(content, className="markdown-content")),
            id=collapse_id,
        ),
        # Tooltip associated with the info icon
        dbc.Tooltip(
            ai_summary_explanation,
            target=info_icon_id,
            placement="right",
            className='custom-tooltip',
            style={'white-space': 'pre-line'}
        )
    ], className="mb-4")
    
    return card


def get_labs_for_single_patient(df_labs, df_vital_signs, df_qols_scores,patient_id="0b11553a-812e-a13b-e3ad-a13c7c4c5e2a"):

    df_labs_patient = df_labs[df_labs.PATIENT==patient_id]
    df_vital_signs_patient = df_vital_signs[df_vital_signs.PATIENT==patient_id]
    df_qols_scores_patient = df_qols_scores[df_qols_scores.PATIENT==patient_id]
    
    return df_labs_patient, df_vital_signs_patient, df_qols_scores_patient

def create_charts_patient(df_labs_patient):

    if df_labs_patient.empty:

        fig = go.Figure()
        fig.add_annotation(text="No Lab Results Available",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=32, color="gray"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return [fig]
    
    else:
        color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        unique_descriptions = df_labs_patient['DESCRIPTION'].unique()
        color_index = 0
        figures = []

        for description in unique_descriptions:
            df_filtered = df_labs_patient[df_labs_patient['DESCRIPTION'] == description]
            unique_units = df_filtered['UNITS'].unique()
            
            if len(unique_units) == 1:
                units = unique_units[0]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_filtered['DATE'],
                    y=df_filtered['VALUE'],
                    mode='lines+markers',
                    name=f'{description} ({units})',
                    line=dict(color=color_palette[color_index])
                ))
                fig.update_layout(template="plotly_dark", title_text=description, showlegend=True,
                                legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top'))
                fig.update_yaxes(title_text=f'{units}')
                figures.append(fig)
                color_index = (color_index + 1) % len(color_palette)

        return figures

def create_collapsible_charts_card(title, figures):
    header_id = "collapse-charts-header"
    collapse_id = "collapse-charts"
    
    button = dbc.Button(
        title,
        color="link",
        className="text-left",
        id=header_id,
        style={'font-size': '2.5rem', 'color': 'white'}
    )
    
    graphs = [dcc.Graph(figure=fig) for fig in figures]
    
    card = dbc.Card([
        dbc.CardHeader(button),
        dbc.Collapse(
            dbc.CardBody(graphs),
            id=collapse_id,
        )
    ], className="mb-4")
    
    return card

def create_vital_signs_charts(df_vital_signs_patient):

    if df_vital_signs_patient.empty:
        fig = go.Figure()
        fig.add_annotation(text="No Vitals Available",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=32, color="gray"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return [fig]

    else:
        fig_bmi = go.Figure()
        fig_bmi.add_trace(go.Scatter(
            x=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Body mass index (BMI) [Ratio]']['DATE'],
            y=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Body mass index (BMI) [Ratio]']['VALUE'],
            mode='lines+markers',
            name='BMI (kg/m2)',
            line=dict(color='#FFA726')  
        ))
        fig_bmi.update_layout(template="plotly_dark", title_text="BMI", showlegend=True,
                                legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
        )
        fig_bmi.update_yaxes(title_text="BMI (kg/m2)")

        

        fig_bp = go.Figure()
        fig_bp.add_trace(go.Scatter(
            x=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Diastolic Blood Pressure']['DATE'],
            y=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Diastolic Blood Pressure']['VALUE'],
            mode='lines+markers',
            name='Diastolic BP (mmHg)',
            line=dict(color='#673AB7')  # First BP trace color
        ))
        fig_bp.add_trace(go.Scatter(
            x=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Systolic Blood Pressure']['DATE'],
            y=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Systolic Blood Pressure']['VALUE'],
            mode='lines+markers',
            name='Systolic BP (mmHg)',
            line=dict(color='#03A9F4')  # Second BP trace color
        ))
        fig_bp.update_layout(template="plotly_dark", title_text="Blood Pressure", showlegend=True,
                                legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
        )
        fig_bp.update_yaxes(title_text="BP (mmHg)")
        # Find the min and max values across both Diastolic and Systolic BP readings
        min_bp = min(df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Diastolic Blood Pressure']['VALUE'].min(), 
                    df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Systolic Blood Pressure']['VALUE'].min())
        max_bp = max(df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Diastolic Blood Pressure']['VALUE'].max(), 
                    df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Systolic Blood Pressure']['VALUE'].max())

        #fig_bp.update_yaxes(range=[min_bp - 10, max_bp + 10])  # Adjust buffer as needed

        

        fig_hr_rr = go.Figure()
        fig_hr_rr.add_trace(go.Scatter(
            x=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Heart rate']['DATE'],
            y=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Heart rate']['VALUE'],
            mode='lines+markers',
            name='Heart Rate (/min)',
            line=dict(color='#D32F2F')  # Heart rate color
        ))
        fig_hr_rr.add_trace(go.Scatter(
            x=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Respiratory rate']['DATE'],
            y=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION'] == 'Respiratory rate']['VALUE'],
            mode='lines+markers',
            name='Respiratory Rate (/min)',
            line=dict(color='#4CAF50')  # Respiratory rate color
        ))

        fig_hr_rr.update_layout(template="plotly_dark", title_text="Heart and Respiratory Rate", showlegend=True,
                                legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top'))

        fig_hr_rr.update_yaxes(title_text="Rate (/min)")
        

        fig_pain = go.Figure()
        fig_pain.add_trace(go.Scatter(
            x=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION']=='Pain severity - 0-10 verbal numeric rating [Score] - Reported']['DATE'],
            y=df_vital_signs_patient[df_vital_signs_patient['DESCRIPTION']=='Pain severity - 0-10 verbal numeric rating [Score] - Reported']['VALUE'],
            mode='lines+markers',
            name='Pain Severity (0-10)',
            line=dict(color='#FFEB3B')  # Adjust as necessary
        ))
        fig_pain.update_layout(
            legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.1, yanchor='top')
        )
        fig_pain.update_layout(template="plotly_dark", title_text="Pain Severity (reported)", showlegend=True)
        fig_pain.update_yaxes(title_text="Pain Severity (0-10, reported)")
        
        return [fig_bmi, fig_bp, fig_hr_rr, fig_pain]

def create_collapsible_vital_signs_card(title, figures):
    header_id = "collapse-vital-signs-header"
    collapse_id = "collapse-vital-signs"
    
    button = dbc.Button(
        title, 
        color="link", 
        className="text-left", 
        id=header_id, 
        style={'font-size': '2.5rem', 'color': 'white'}
    )
    
    graphs = [dcc.Graph(figure=fig) for fig in figures]
    
    card = dbc.Card([
        dbc.CardHeader(button),
        dbc.Collapse(
            dbc.CardBody(graphs),
            id=collapse_id,
        )
    ], className="mb-4")
    
    return card

# QOLS
def create_qols_chart(df_qols_scores_patient):

    if df_qols_scores_patient.empty:
        fig = go.Figure()
        fig.add_annotation(text="No Quality of Life Data Available",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=32, color="gray"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    else:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_qols_scores_patient['DATE'],
            y=df_qols_scores_patient['VALUE'],
            mode='lines+markers',
            name='QOLS Score'
        ))

        fig.update_layout(
            title='QOLS Scores',
            xaxis_title='Date',
            yaxis_title='QOLS Score',
            template="plotly_dark"
        )
        fig.update_yaxes(range=[0, 1])  

        return fig

def create_collapsible_qols_card(title, figure):
    header_id = "collapse-qols-header"
    collapse_id = "collapse-qols"
    
    button = dbc.Button(
        title, 
        color="link", 
        className="text-left", 
        id=header_id, 
        style={'font-size': '2.5rem', 'color': 'white'}
    )
    
    graph = dcc.Graph(figure=figure)
    
    card = dbc.Card([
        dbc.CardHeader(button),
        dbc.Collapse(
            dbc.CardBody(graph),
            id=collapse_id,
        )
    ], className="mb-4")
    
    return card


def create_updated_ai_patient_view(random_patient_id="e154f937-18c5-ebaa-1fd0-0b714169d18b"):
    
    patient_id_title = html.H3(f"Patient ID: {random_patient_id}", style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'})

    patient_summary = load_patient_summary(random_patient_id)
    summary_card = create_collapsible_summary_card("AI Patient Summary", patient_summary)

    df_labs_patient, df_vital_signs_patient, df_qols_scores_patient = get_labs_for_single_patient(df_labs, df_vital_signs, df_qols_scores, random_patient_id)
    
    vital_signs_figures = create_vital_signs_charts(df_vital_signs_patient)
    vital_signs_card = create_collapsible_vital_signs_card("Vitals", vital_signs_figures)
    
    lab_figures = create_charts_patient(df_labs_patient)
    labs_card = create_collapsible_charts_card("Lab Results", lab_figures)

    qols_figure = create_qols_chart(df_qols_scores_patient)
    qols_card = create_collapsible_qols_card("Quality of Life", qols_figure)

    return patient_id_title, summary_card, vital_signs_card, labs_card, qols_card

