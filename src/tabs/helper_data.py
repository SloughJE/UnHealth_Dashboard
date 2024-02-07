unhealth_score_explanation = """The UnHealth Score:
• Combines multiple health indicators from CDC PLACES data into 1 metric
• Range from 0 to 100, higher is more UnHealthy
• Includes chronic diseases, lifestyle factors, prevention, and disabilities
• Each indicator is weighted; indicators like stroke, diabetes, and cancer have high impact; others like sleep duration, lower impact
• Economic data is not factored into the UnHealth score
"""

CDC_PLACES_help = """CDC's PLACES is a public health initiative providing local health data across the US, focusing on chronic diseases, health outcomes, and behaviors at community levels (counties, cities, ZIP codes).
Data is shown as percentages of population.
e.g. for the Measure 'Sleeping < 7 hours (>=18)', in the county of Aroostook, Maine a value of 34.6% indicates that 34.6% of adults 18 or over sleep less than 7 hours per night, according to a CDC survey."""



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