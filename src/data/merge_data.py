import os
import json

import pandas as pd
import geopandas as gpd
from shapely import wkt

def merge_gdp_ranking_data(year, gdp_filepath, ranking_filepath, spending_filepath):

    df_gdp = pd.read_pickle(gdp_filepath)
    df_ranking = pd.read_pickle(ranking_filepath)
    df_spending = pd.read_pickle(spending_filepath)

    df_ranking = df_ranking[df_ranking.Year==year]
    merged_df = pd.merge(df_ranking, df_gdp, left_on=['GEOID'],right_on=['GeoFips'], how='left')
    merged_df = pd.merge(merged_df, df_spending, left_on=['GEOID'],right_on=['shape_code'], how='inner')
    merged_df['GDP_Per_Capita_2020'] = merged_df['gdp'] / merged_df['population']

    cols_wanted = ['Year','GEOID','LocationName','StateDesc','StateAbbr','Weighted_Score_Normalized','Rank','population','GDP_Per_Capita_2020']
    merged_df = merged_df[cols_wanted]
    filepath_out = "data/processed/HealthScore_Rank_GDP_Pop_perCounty.pickle"
    merged_df.to_pickle(filepath_out)
    print(merged_df.head())
    print(f"data shape: {merged_df.shape}")

    print(f"file saved to: {filepath_out}")
