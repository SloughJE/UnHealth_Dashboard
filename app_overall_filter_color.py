import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format, Group

import plotly.graph_objects as go
import pandas as pd
import json

from pygam import LinearGAM, s
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Style for the data table
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
        'if': {'column_id': 'population'},
        'textAlign': 'right'
    },
    {
        'if': {'column_id': 'GDP_Per_Capita_2020'},
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
        'if': {'column_id': 'population'},
        'textAlign': 'right',
        'width': '15%',  

    },
    {
        'if': {'column_id': 'GDP_Per_Capita_2020'},
        'textAlign': 'right',
        'width': '15%',  

    }
]

### Load data#####
df_ranking = pd.read_pickle("data/processed/HealthScore_Rank_GDP_Pop_perCounty.pickle")
df_ranking = df_ranking[df_ranking.Year==2020]

# merged_df = pd.read_pickle("data/processed/HealthScore_Rank_GDP_Pop_perCounty.pickle")
merged_df = df_ranking.copy()
merged_df = merged_df[['GEOID','LocationName','StateDesc','StateAbbr','Weighted_Score_Normalized', 'Rank', 'GDP_Per_Capita_2020','population']]

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)
############

# Calculate IQR for 'GDP_Per_Capita_2020'

percentile_low = df_ranking['Weighted_Score_Normalized'].quantile(0.05)
percentile_high = df_ranking['Weighted_Score_Normalized'].quantile(0.95)
percentile_low_scatter = percentile_low
percentile_high_scatter = percentile_high
####################
####BUBBLE CHART####
####################


# Calculate IQR for 'GDP_Per_Capita_2020'
Q1 = merged_df['GDP_Per_Capita_2020'].quantile(0.01)
Q3 = merged_df['GDP_Per_Capita_2020'].quantile(0.99)
IQR = Q3 - Q1

# Define bounds for outliers
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter out outliers
merged_df = merged_df[(merged_df['GDP_Per_Capita_2020'] >= lower_bound) & (merged_df['GDP_Per_Capita_2020'] <= upper_bound)]
merged_df['Weighted_Score_Normalized'] = round(merged_df.Weighted_Score_Normalized,2)


# Fit a GAM model
# Apply logarithmic transformation and then scale to the range [0, 1]
normalized_weights = np.log(merged_df['population'] + 1)  # Add 1 to avoid log(0)
#normalized_weights = (normalized_weights - normalized_weights.min()) / (normalized_weights.max() - normalized_weights.min())
# Fit the GAM model with normalized weights
gam = LinearGAM(s(0, n_splines=20, constraints='monotonic_inc', lam=10))
#gam.fit(merged_df[['GDP_Per_Capita_2020']], merged_df['Weighted_Score_Normalized'], weights=normalized_weights)
gam.fit(merged_df[['GDP_Per_Capita_2020']], merged_df['Weighted_Score_Normalized'])

# Generate predictions and intervals as before
x_pred = pd.DataFrame({'GDP_Per_Capita_2020': np.linspace(merged_df['GDP_Per_Capita_2020'].min(), merged_df['GDP_Per_Capita_2020'].max(), 500)})
y_pred = gam.predict(x_pred)

# Calculate the quintile boundaries
quintiles = merged_df['Weighted_Score_Normalized'].quantile([0.2, 0.4, 0.6, 0.8]).values

# Function to determine quintile number
def get_quintile_number(score, quintiles):
    if score <= quintiles[0]:
        return 1
    elif score <= quintiles[1]:
        return 2
    elif score <= quintiles[2]:
        return 3
    elif score <= quintiles[3]:
        return 4
    else:
        return 5

# Assign quintile number to each data point
merged_df['quintile'] = merged_df['Weighted_Score_Normalized'].apply(
    lambda score: get_quintile_number(score, quintiles)
)

# Custom colorscale based on quintiles
quintile_colorscale = {
    1: "darkred",
    2: "orange",
    3: "yellow",
    4: "lightgreen",
    5: "darkgreen"
}
original_colors = [quintile_colorscale[q] for q in merged_df['quintile']]
merged_df['original_colors'] = original_colors
#original_sizes = merged_df.population
# Apply the colorscale to the scatter plot

def create_updated_bubble_chart(selected_state):

    # Always start with the full dataset
    filtered_df = merged_df.copy()

    # Step 1: Filter by State (if any are selected)
    if selected_state:
        filtered_df = filtered_df[filtered_df['StateAbbr'].isin(selected_state)]

    hover_text = [
    f"{row['LocationName']}, {row['StateDesc']}<br>County Health Score: {row['Weighted_Score_Normalized']}<br>Rank: {row['Rank']}<br>GDP Per Capita: {row['GDP_Per_Capita_2020']}<br>Population: {row['population']}"
    for index, row in filtered_df.iterrows()
]
    
    fig_bubble = go.Figure()
    # Check if there is data after filtering
    if len(filtered_df) == 0:
        # If no data, display a message
        fig_bubble.update_layout(
            xaxis={'visible': False},  # Hide x axis
            yaxis={'visible': False},  # Hide y axis
            annotations=[
                {
                    'text': 'No data available for this state or county',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20}
                }
            ],
            paper_bgcolor="black",  # Background color
            plot_bgcolor="black",  # Plot area background color
            font=dict(color="white"),  # Text color
        )
    else:
        scatter_plot = go.Scatter(
            x=filtered_df['GDP_Per_Capita_2020'],
            y=filtered_df['Weighted_Score_Normalized'],
            mode='markers',
            marker=dict(
                color=list(filtered_df['Weighted_Score_Normalized']),  # The variable for color scale
                colorscale='RdYlGn',  # Red-Yellow-Green color scale
                cmin=percentile_low_scatter,  # 5th percentile
                cmax=percentile_high_scatter,  # 95th percentile
                line=dict(
                    width=.2,
                    color='black'
                )
            ),
            text=hover_text,
            hoverinfo='text',
            customdata=filtered_df['GEOID'],
            name='County'
        )


        # Add the GAM trend line
        trend_line = go.Scatter(x=x_pred['GDP_Per_Capita_2020'], y=y_pred, mode='lines', 
                                name='GAM Trend Line', 
                                line=dict(color='darkgrey', width=5))

        # Add prediction intervals
        y_intervals = gam.prediction_intervals(x_pred, width=0.8)
        lower_interval = go.Scatter(
            x=x_pred['GDP_Per_Capita_2020'],
            y=y_intervals[:, 0],
            mode='lines',
            line=dict(color='lightgrey', width=1, dash='dot'),  # Lighter color, dashed line
            name='Lower Interval',
            showlegend=False
        )

        upper_interval = go.Scatter(
            x=x_pred['GDP_Per_Capita_2020'],
            y=y_intervals[:, 1],
            fill='tonexty',
            mode='lines',
            line=dict(color='lightgrey', width=1, dash='dot'),  # Lighter color, dashed line
            name='95% Prediction Interval',
            fillcolor='rgba(150, 150, 150, 0.3)',  # Light fill color with reduced opacity
            showlegend=True
        )

        fig_bubble.add_trace(scatter_plot)
        fig_bubble.add_trace(lower_interval)
        fig_bubble.add_trace(upper_interval)
        fig_bubble.add_trace(trend_line)

        # Update the layout for a dark and minimalist theme
        fig_bubble.update_layout(
            title='GDP per Capita vs Health Score',
            title_x=0.5,  # Center the title
            title_font=dict(size=20),  # Adjust the font size if needed
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(title='GDP per capita 2020', range=[0, 200000], showgrid=False, linecolor='darkgrey', linewidth=1),  # Hide grid lines and set axis line color
            yaxis=dict(range=[0, 101], showgrid=False, linecolor='darkgrey', linewidth=1),  # Hide grid lines and set axis line color
            yaxis_title='Health Score',
            #width=700, height=600,
            coloraxis_showscale=False,
            
            legend=dict(
                x=0.74,
                y=.05,
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="white"
                ),
                bordercolor="gray",
                borderwidth=1
            ),
            paper_bgcolor="black",  # Background color
            plot_bgcolor="black",  # Plot area background color
            font=dict(color="white"),  # Text color
        )

    fig_bubble.update_layout(
        autosize=True,  # Enable autosize
    )
    return fig_bubble


####################
###### MAP #########
####################




# selected_year = 2020
# merged_df_county_map = df_ranking[(df_ranking['Year'] == selected_year)]
num_counties = len(df_ranking)

# Calculate the quintile boundaries
quintiles = df_ranking['Weighted_Score_Normalized'].quantile([0.2, 0.4, 0.6, 0.8]).values

# Function to determine quintile number
def get_quintile_number(score, quintiles):
    if score <= quintiles[0]:
        return 1
    elif score <= quintiles[1]:
        return 2
    elif score <= quintiles[2]:
        return 3
    elif score <= quintiles[3]:
        return 4
    else:
        return 5

# Assign quintile number to each row
df_ranking['quintile'] = df_ranking['Weighted_Score_Normalized'].apply(
    lambda score: get_quintile_number(score, quintiles)
)

# Create separate dataframes for each quintile
#quintile_dfs = []
#for i in range(1, 6):
#    quintile_dfs.append(df_ranking[df_ranking['quintile'] == i])

# Custom colorscale based on quintiles
quintile_colorscale = ["darkred", "orange", "yellow", "green", "darkgreen"]


def create_updated_map(selected_state):
    # Initialize an empty list to store filtered DataFrames
    filtered_dfs = []

    # Iterate through the list of dataframes
    # Filter the dataframe based on selected_state (if it's not None)
    if selected_state is not None and len(selected_state) > 0:
        filtered_df_by_state = df_ranking[df_ranking['StateAbbr'].isin(selected_state)]
    else:
        filtered_df_by_state = df_ranking  # No state filter applied

    fig = go.Figure()

    #for i, quintile_df in enumerate(filtered_dfs):
    fig.add_trace(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df_by_state['GEOID'],
        z=filtered_df_by_state.Weighted_Score_Normalized,  # Assign a constant value for color for each quintile
        colorscale="RdYlGn",
        #name=f"Quintile {i+1}",
        #legendgroup=f"quintile{i+1}",
        customdata=filtered_df_by_state[['GEOID', 'LocationName', 'StateAbbr', 'Rank', 'Weighted_Score_Normalized','quintile']],
        hovertemplate = '%{customdata[1]} County, %{customdata[2]}<br>Score: %{customdata[4]:.2f}<br>Rank: %{customdata[3]} of ' + str(num_counties) + '<extra>Quintile: %{customdata[5]}</extra>',
        marker_line_width=0,
        colorbar=dict(
            thickness=15,
            len=0.5,
            tickformat="0",
            x=0.05,  # Adjust this value to move the colorbar closer
            xpad=0,  # Adjust padding if needed
            tickfont=dict(color='white'),  # Set tick font color
        ),
        zmin=percentile_low,
        zmax=percentile_high,
        showscale=True,
        name=""
        )
    )

    fig.update_layout(
        geo=dict(
            scope="usa",
            lakecolor='black',
            landcolor='black',
            bgcolor='black',
            subunitcolor='darkgrey',
            showlakes=True,
            showsubunits=True,
            showland=True,
            showcountries=False,
            showcoastlines=True,
            countrycolor='darkgrey',
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        title_text='Health Score',
        title_x=0.5,  # Center the title
        margin=dict(l=0, r=0, t=40, b=0),
        title_font=dict(size=20, color='white'),
        
    )

    fig.add_annotation(
        text="Color scale represents<br>5th to 95th percentile",
        align='left',
        showarrow=False,
        xref='paper', yref='paper',
        x=0.95, y=0.15,
        bgcolor="black",  # Set background color
        bordercolor="gray",  # Set border color
        borderpad=4,
        font=dict(color='white')  # Set text color
    )

    fig.update_layout(
        autosize=True,  # Enable autosize
        #margin=dict(l=0, r=0, t=0, b=0)  # Remove margin
    )
    return fig

print("loading app")

# Extract unique states and counties from your data
available_states = df_ranking['StateAbbr'].unique()
available_states.sort()
#available_counties = df_ranking['LocationName'].unique()

def find_top_bottom_values(df, column_name, max_values):
    # Sort the DataFrame based on a column
    sorted_df = df.sort_values(by=column_name)

    # Select the top and bottom values
    bottom_df = sorted_df.head(max_values)
    top_df = sorted_df.tail(max_values)

    # Combine both top and bottom DataFrames
    combined_df = pd.concat([bottom_df, top_df])

    return combined_df

def value_to_color(value, min_val, max_val, colormap=plt.cm.RdYlGn):
    """Convert a value to a color using a matplotlib colormap."""
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
    return mcolors.to_hex(colormap(norm(value)))


# Initialize the Dash app
app = dash.Dash(__name__)

# Custom CSS to reset default browser styles
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

# Define the app layout with responsive design
app.layout = html.Div([
    html.H1("Overall Health Score and GDP per Capita by County for 2020", style={
        'color': 'white',
        'textAlign': 'center',
        'fontSize': '42px',
        'margin': '0',
        'padding': '20px 0'
    }),

    html.Div([
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in available_states],
            multi=True,
            placeholder='Select a State or States',
            style={
                'color': '#212121',  # Text color
                'backgroundColor': '#303030',  # Dropdown background color
                'borderRadius': '5px',  # Rounded corners
                'fontSize': '20px',
            }
        )
    ], style={
        'width': '30%',
        'margin': 'auto',
        'padding': '20px 0',
        'border': 'none',  # Remove any border from the parent div
        'backgroundColor': 'transparent',  # Ensure background is transparent
    }),

    # Map and Bubble Chart with adjusted padding
    html.Div([
        html.Div([
            dcc.Graph(id='choropleth-map', figure={})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '0', 'height': '80vh', 'marginBottom': '0'}),
        html.Div([
            dcc.Graph(id='bubble-chart', figure={})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '0', 'height': '80vh', 'marginBottom': '0'})
    ], style={'display': 'flex', 'backgroundColor': 'black', 'flexWrap': 'wrap','padding':'0', 'marginBottom': '0'}), 

    # Title for Table
    html.Div(
        html.H2("Ten Worst and Best County Health Scores", style={
            'color': 'white',
            'textAlign': 'center',
            'fontSize': '30px',
            'marginTop': '0',
            'marginBottom': '0',
            'textDecoration': 'none',
            'borderBottom': 'none',
            'backgroundColor': 'black',
            'padding': '0'
        }),
        style={
            'backgroundColor': 'black',
            'border': 'none',
            'margin': '0',
            'padding': '0'
        }
    ),

    # Data Table
    html.Div([
        dash_table.DataTable(
            id='state-data-table',
            columns=[
                {"name": "County", "id": "LocationName"},
                {"name": "State", "id": "StateDesc"},
                {
                    "name": "GDP per Capita", 
                    "id": "GDP_Per_Capita_2020",
                    "type": "numeric", 
                    "format": Format(group=Group.yes)  # Group by thousands
                },
                {
                    "name": "Population", 
                    "id": "population",
                    "type": "numeric", 
                    "format": Format(group=Group.yes)  # Group by thousands
                },
                {"name": "Health Score", "id": "Weighted_Score_Normalized"},
                {"name": "Overall Rank", "id": "Rank"},
            ],
            data=[],
            style_cell_conditional=style_cell_conditional,
            style_header_conditional=style_header_conditional,
            **table_style
        )
    ], style={'textAlign': 'center', 'backgroundColor': 'black', 'padding': '20px', 'border': 'none'})

], style={
    'backgroundColor': 'black',
    'margin': '0',
    'padding': '0',
    'height': '100vh',
    'border': 'none'
})

# Define callback to update map and chart based on user input
@app.callback(
    [Output('choropleth-map', 'figure'), Output('bubble-chart', 'figure')],
    [Input('state-dropdown', 'value')]
)
def update_map_and_chart(selected_state):
    # Filter your data based on selected_state and 
    # Update the map and bubble chart based on the filtered data

    # Create and return the updated figures for map and bubble chart
    updated_map_fig = create_updated_map(selected_state)
    updated_bubble_chart_fig = create_updated_bubble_chart(selected_state)

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
        filtered_df = df_ranking[df_ranking['StateAbbr'].isin(selected_state)]
    else:
        # If no state is selected, use the full dataset
        filtered_df = df_ranking
    # Get top and bottom values based on filtered DataFrame
    top_bottom_df = find_top_bottom_values(filtered_df, 'Weighted_Score_Normalized', max_values)
    # Calculate colors for each row in the top_bottom_df based on overall min and max values
    top_bottom_df['Color'] = top_bottom_df['Weighted_Score_Normalized'].apply(lambda x: value_to_color(x, percentile_low, percentile_high))
    top_bottom_df['Weighted_Score_Normalized'] = round(top_bottom_df.Weighted_Score_Normalized,2)

    top_bottom_df['GDP_Per_Capita_2020'] = round(top_bottom_df.GDP_Per_Capita_2020,0)
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



if __name__ == '__main__':
    app.run_server(debug=True)