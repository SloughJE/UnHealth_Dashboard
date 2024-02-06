
unhealth_score_explanation = """
The UnHealth Score™ provides a comprehensive overview of a county's health by combining data on various health indicators, such as the prevalence of chronic diseases, lifestyle factors, and disabilities. A higher UnHealth Score corresponds to a greater prevalence of unfavorable health indicators. Each indicator is assigned an impact score, reflecting its significance on public health. High-impact indicators include stroke, diabetes, and cancer, among others, while lower-impact indicators cover aspects like sleep duration and health screenings.


The process involves normalizing data across all indicators to create a score out of 100, where a higher score signals more significant health challenges within the county. This normalized score allows for direct comparison across counties, offering insights into areas needing most health-related interventions and support.
"""

CDC_PLACES_help = """
CDC's PLACES is a public health initiative that provides detailed local health data across the US. It offers insights into chronic diseases, health outcomes, and behaviors at the community level, including counties, cities, and ZIP codes. The project supports informed public health decisions by highlighting health disparities and guiding resource allocation to improve community health and reduce inequalities.
The data for CDC's PLACES comes from several sources, including the Behavioral Risk Factor Surveillance System (BRFSS), which is a nationwide health-related telephone survey. The project uses advanced statistical methods to extrapolate and estimate health-related measures for smaller geographic areas, such as census tracts and ZIP Code Tabulation Areas (ZCTAs), from this larger dataset. These methods allow PLACES to provide detailed local health data even for areas not directly surveyed, ensuring comprehensive coverage across the United States.
The data mainly comes from 2019-2022. When there are the same measures for multiple years, we show the most recent.
"""


common_div_style = {
    'backgroundColor': 'black', 
    'padding': '10px', 
    'border-radius': '5px',
    'margin-bottom': '20px'  
}

centered_div_style = {
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'justifyContent': 'center',
}

# Style for the data table in Overall View
table_style = {
    'style_table': {
        'overflowX': 'auto',
        'width': '50%',
        'margin': 'auto',
        'border': '1px solid white'
    },
    'style_cell': {
        #'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'black',
        'border': '1px solid grey',
        'textAlign': 'center',
        'padding': '5px',
        'fontWeight': 'bold',

    },
    'style_header': {
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'border': '1px solid grey',
        'fontWeight': 'bold',
        'textAlign': 'center'
    }
}


style_header_conditional=[
    {
        'if': {'column_id': 'Weighted_Score_Normalized'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'Rank'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'LocationName'},
        'textAlign': 'center'
    },
    {
        'if': {'column_id': 'StateDesc'},
        'textAlign': 'center'
    },
    {
        'if': {'column_id': 'Population'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'Per capita personal income'},
        'textAlign': 'right'
    }
]


style_cell_conditional=[
    {
        'if': {'column_id': 'Weighted_Score_Normalized'},
        'width': '15%',  
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'Rank'},
        'width': '10%',  
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'LocationName'},
        'textAlign': 'left'
    },
    {
        'if': {'column_id': 'StateDesc'},
        'textAlign': 'left'
    },
        {
        'if': {'column_id': 'Population'},
        'textAlign': 'right',
        'width': '15%',  

    },
    {
        'if': {'column_id': 'Per capita personal income'},
        'textAlign': 'right',
        'width': '15%',  

    }
]