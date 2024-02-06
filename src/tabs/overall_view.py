
import plotly.graph_objects as go
import pandas as pd
import json

from pygam import LinearGAM, s
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


### Load data#####
df_ranking = pd.read_pickle("data/processed/df_summary_final.pickle")
num_counties = len(df_ranking)

# GeoJSON file
file_path_geo_json = "data/interim/us_census_counties_geojson.json"
with open(file_path_geo_json) as f:
    counties = json.load(f)

min_x = df_ranking['Per capita personal income'].min()

# Calculate IQR for 'Per capita personal income'

percentile_low = df_ranking['Weighted_Score_Normalized'].quantile(0.05)
percentile_high = df_ranking['Weighted_Score_Normalized'].quantile(0.95)
percentile_low_scatter = percentile_low
percentile_high_scatter = percentile_high


# FILTER outliers based on IQR
def filter_outliers(df):
    # not used
    Q1 = df['Per capita personal income'].quantile(0.01)
    Q3 = df['Per capita personal income'].quantile(0.99)
    IQR = Q3 - Q1

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out outliers
    df = df[(df['Per capita personal income'] >= lower_bound) & (df['Per capita personal income'] <= upper_bound)]
    df['Weighted_Score_Normalized'] = round(df.Weighted_Score_Normalized,2)
    
    return df

def fit_gam(df):
    # Fit a GAM model
    gam = LinearGAM(s(0, n_splines=20, lam=2, constraints='monotonic_dec'))
    gam.fit(df[['Per capita personal income']], df['Weighted_Score_Normalized'])
    # Get the summary of the GAM model
    #gam_summary = gam.summary()
    # Extract the R-squared (R2) value from the summary
    pseudo_r2_value = gam.statistics_['pseudo_r2']['explained_deviance']
    #print(gam.summary())
    #print(pseudo_r2_value)
    # Generate predictions and intervals as before
    x_pred = pd.DataFrame({'Per capita personal income': np.linspace(df['Per capita personal income'].min(), df['Per capita personal income'].max(), 500)})
    y_pred = gam.predict(x_pred)
    y_intervals = gam.prediction_intervals(x_pred, width=0.8)
    y_intervals[:, 0] = np.maximum(y_intervals[:, 0], 0)  # Set lower bounds to 0 if they are below 0
    
    # Plot the residuals
    #residuals = df['Weighted_Score_Normalized'] - gam.predict(df[['Per capita personal income']])
    #plt.figure(figsize=(10, 6))
    #plt.scatter(x, residuals, facecolors='none', edgecolors='r')
    #plt.axhline(y=0, color='k', linestyle='--')
    #plt.xlabel('Feature Value')
    #plt.ylabel('Residuals')
    #plt.title('Residual Plot for GAM')
    #plt.grid(True)
    # Save the plot
    #plt.savefig('gam_residuals.png')

    return x_pred, y_pred, y_intervals, pseudo_r2_value

#df_gam = filter_outliers(df_gam)
x_pred, y_pred, y_intervals, pseudo_r2_value = fit_gam(df_ranking)


def create_updated_scatter_chart(df,selected_state,x_pred, y_pred, y_intervals, pseudo_r2_value):

    # Always start with the full dataset
    filtered_df = df.copy()

    # Step 1: Filter by State (if any are selected)
    if selected_state:
        filtered_df = filtered_df[filtered_df['StateDesc'].isin(selected_state)]

    hover_text = [
        f"{row['LocationName']}, {row['StateDesc']}<br>UnHealth Score: {row['Weighted_Score_Normalized']:.2f}<br>Rank: {row['Rank']:,.0f} of {num_counties}<br>Per capita personal income: {row['Per capita personal income']:,.0f}<br>Population: {row['Population']:,.0f}<br>{row['Note']}"
        for index, row in filtered_df.iterrows()
    ]

    
    fig_scatter = go.Figure()
    # Check if there is data after filtering
    if len(filtered_df) == 0:
        # If no data, display a message
        fig_scatter.update_layout(
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
            x=filtered_df['Per capita personal income'],
            y=filtered_df['Weighted_Score_Normalized'],
            mode='markers',
            marker=dict(
                color=list(filtered_df['Weighted_Score_Normalized']),  # The variable for color scale
                colorscale='RdYlGn_r',  # Red-Yellow-Green color scale
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
        trend_line = go.Scatter(x=x_pred['Per capita personal income'], y=y_pred, mode='lines', 
                                name='GAM Model (all counties)', 
                                line=dict(color='darkgrey', width=5),
                                hovertemplate='Per capita personal income: %{x:,.0f}<br>UnHealth Score (predicted): %{y:.2f}<br>GAM Model Pseudo R²: ' + str(round(pseudo_r2_value, 2))
)

        # Add prediction intervals
        lower_interval = go.Scatter(
            x=x_pred['Per capita personal income'],
            y=y_intervals[:, 0],
            mode='lines',
            line=dict(color='lightgrey', width=1, dash='dot'),  # Lighter color, dashed line
            name='Lower Interval',
            showlegend=False
        )

        upper_interval = go.Scatter(
            x=x_pred['Per capita personal income'],
            y=y_intervals[:, 1],
            fill='tonexty',
            mode='lines',
            line=dict(color='lightgrey', width=1, dash='dot'),  # Lighter color, dashed line
            name='80% Prediction Interval',
            fillcolor='rgba(150, 150, 150, 0.3)',  # Light fill color with reduced opacity
            showlegend=True
        )

        fig_scatter.add_trace(scatter_plot)
        fig_scatter.add_trace(lower_interval)
        fig_scatter.add_trace(upper_interval)
        fig_scatter.add_trace(trend_line)

        # Update the layout for a dark and minimalist theme
        fig_scatter.update_layout(
            height=600,
            title='Income per Capita and UnHealth Score',
            title_x=0.5,  # Center the title
            title_font=dict(size=24),  # Adjust the font size if needed
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(title='Income per Capita',range=[min_x,200000], showgrid=False, linecolor='darkgrey', linewidth=1),  # Hide grid lines and set axis line color
            yaxis=dict(range=[0, 101], showgrid=False, linecolor='darkgrey', linewidth=1),  # Hide grid lines and set axis line color
            yaxis_title='UnHealth Score',
            #width=700, height=600,
            coloraxis_showscale=False,
            
            legend=dict(
                x=0.74,
                y=.90,
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
    fig_scatter.update_xaxes(zeroline=True, zerolinewidth=0.5, zerolinecolor="gray")
    fig_scatter.update_yaxes(zeroline=True, zerolinewidth=0.5, zerolinecolor="gray")

    fig_scatter.update_layout(
        autosize=False,  # Enable autosize
    )
    return fig_scatter


####################
###### MAP #########
####################

def create_updated_map(df, selected_state):
    
    # Filter the dataframe based on selected_state (if it's not None)
    if selected_state is not None and len(selected_state) > 0:
        filtered_df_by_state = df[df['StateDesc'].isin(selected_state)]
    else:
        filtered_df_by_state = df  # No state filter applied

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        geojson=counties,
        featureidkey="properties.GEOID",
        locations=filtered_df_by_state['GEOID'],
        z=filtered_df_by_state.Weighted_Score_Normalized,
        colorscale="RdYlGn_r",
        customdata=filtered_df_by_state[['GEOID', 'LocationName', 'StateDesc', 'Rank', 'Weighted_Score_Normalized','Per capita personal income','Population','Note']],
        hovertemplate = (
            '%{customdata[1]}, %{customdata[2]}<br>'
            'UnHealth Score: %{customdata[4]:.2f}<br>'
            'Rank: %{customdata[3]} of ' + str(num_counties) + '<br>'
            'Per capita personal income: %{customdata[5]:,.0f}<br>'
            'Population: %{customdata[6]:,.0f}<br>'
            '%{customdata[7]}'
        ),
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
        height=600,
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
        title_text='UnHealth Score',
        title_x=0.5,  # Center the title
        margin=dict(l=0, r=0, t=40, b=0),
        title_font=dict(size=24, color='white'),
        
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
        autosize=False,  # Enable autosize
        #margin=dict(l=0, r=0, t=0, b=0)  # Remove margin
    )
    return fig



# Extract unique states and counties from your data
available_states = df_ranking['StateDesc'].unique()
available_states.sort()

def find_top_bottom_values(df, column_name, max_values):
    # Sort the DataFrame based on a column
    sorted_df = df.sort_values(by=column_name)

    # Select the top and bottom values
    bottom_df = sorted_df.head(max_values)
    top_df = sorted_df.tail(max_values)

    # Combine both top and bottom DataFrames
    combined_df = pd.concat([bottom_df, top_df])

    return combined_df

def value_to_color(value, min_val, max_val, colormap=plt.cm.RdYlGn_r):
    """Convert a value to a color using a matplotlib colormap."""
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
    return mcolors.to_hex(colormap(norm(value)))

