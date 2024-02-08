import pandas as pd

from src.data.measures_dicts import measure_replacements, impact_scores


def process_cdc_data(CDC_filepath: str) -> None:
    """
    Processes CDC data to normalize and weight scores by measure, then ranks counties based on these scores.

    Args:
        CDC_filepath (str): File path to the CDC data pickle file.

    Returns:
        None: Saves two pickle files, one with county measures and another with county rankings.
    """
        


    df = pd.read_pickle(CDC_filepath)
    df = df[df['LocationName'] != df['StateDesc']]  # Remove state data if any
    df = df.sort_values('Year', ascending=False).groupby(['GEOID', 'Measure']).first().reset_index()
    df.drop_duplicates(inplace=True)

    def normalize_within_group(df, column_name):
        min_val = df[column_name].min()
        max_val = df[column_name].max()
        df[column_name + '_Normalized'] = ((df[column_name] - min_val) / (max_val - min_val)) * 100
        return df
    

    df = df.groupby('Measure').apply(lambda x: normalize_within_group(x, 'Data_Value')).reset_index(drop=True)

    df['Weighted_Score'] = df.apply(lambda row: row['Data_Value_Normalized'] * impact_scores.get(row['Measure'], 0), axis=1)

    county_scores = df.groupby(['GEOID', 'LocationName', 'StateDesc', 'StateAbbr'])['Weighted_Score'].sum().reset_index()
    county_scores = normalize_within_group(county_scores, 'Weighted_Score')

    # Add a ranking column based on the normalized weighted score
    county_scores['Rank'] = county_scores['Weighted_Score_Normalized'].rank(ascending=True, method='min')
    county_scores['Rank'] = county_scores['Rank'].astype(int)
    county_scores = county_scores.sort_values(by='Rank')

    df = pd.merge(df,county_scores[['GEOID','Weighted_Score','Weighted_Score_Normalized','Rank']].rename(columns={'Weighted_Score':'Weighted_Score_Overall'}),on='GEOID',how='left')
    df['percent_contribution'] = (df.Weighted_Score/df.Weighted_Score_Overall)
    df['absolute_contribution'] = (df.Weighted_Score_Normalized*df.percent_contribution)

    df['Measure_short'] = df['Measure'].replace(measure_replacements)

    fips_county = '01011' # for example 
    print(f"example data for fips: {fips_county}")
    print(df[(df.GEOID==fips_county)].head(2))
    print(f"Summed CHS: {df[(df.GEOID==fips_county)].absolute_contribution.sum()}")

    print(county_scores[(county_scores.GEOID==fips_county)])
    print(f"df county measures shape: {df.shape}")
    print(f"county_scores shape: {county_scores.shape}")

    output_filepath = "data/processed/CDC_PLACES_county_measures.pickle"
    df.to_pickle(output_filepath)
    print(f"file saved to: {output_filepath}")

    output_filepath = "data/processed/CDC_PLACES_county_rankings.pickle"
    county_scores.to_pickle(output_filepath)
    print(f"file saved to: {output_filepath}")
