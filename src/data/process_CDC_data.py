import pandas as pd
import numpy as np

def process_cdc_data(CDC_filepath):
    
    impact_scores = {
        "Stroke among adults aged >=18 years": 5,
        "Chronic obstructive pulmonary disease among adults aged >=18 years": 5,
        "Cancer (excluding skin cancer) among adults aged >=18 years": 5,
        "Diagnosed diabetes among adults aged >=18 years": 5,
        "Coronary heart disease among adults aged >=18 years": 5,
        "Chronic kidney disease among adults aged >=18 years": 5,
        "Cognitive disability among adults ages >=18 years": 5,
        "Self-care disability among adults aged >=18 years": 5,

        "Current smoking among adults aged >=18 years": 4,
        "Obesity among adults aged >=18 years": 4,
        "Depression among adults aged >=18 years": 4,
        "Binge drinking among adults aged >=18 years": 4,
        "Mental health not good for >=14 days among adults aged >=18 years": 4,
        "Mobility disability among adults aged >=18 years": 4,
        "High blood pressure among adults aged >=18 years": 4,
        "Independent living disability among adults aged >=18 years": 4,
        "Vision disability among adults aged >=18 years": 4,
        "Any disability among adults aged >=18 years": 4,

        "Arthritis among adults aged >=18 years": 3,
        "No leisure-time physical activity among adults aged >=18 years": 3,
        "Physical health not good for >=14 days among adults aged >=18 years": 3,
        "Fair or poor self-rated health status among adults aged >=18 years": 3,
        "All teeth lost among adults aged >=65 years": 3,
        "Current lack of health insurance among adults aged 18-64 years": 3,

        "High cholesterol among adults aged >=18 years who have been screened in the past 5 years": 2,
        "Sleeping less than 7 hours among adults aged >=18 years": 2,
        "Current asthma among adults aged >=18 years": 2,
        "Not taking medicine for high blood pressure among adults aged >=18 years": 2,
        "Older adult men aged >=65 years not up to date on clinical preventive services": 2,
        "Older adult women aged >=65 years not up to date on clinical preventive services": 2,

        "No mammography use among women aged 50-74 years": 1,
        "No colorectal cancer screening among adults aged 50-75 years": 1,
        "No cervical cancer screening among adult women aged 21-65 years": 1,
        "No doctor visit for checkup in past year among adults aged >=18 years": 1,
        "No dental visit in past year among adults aged >=18 years": 1,
        "No cholesterol screening among adults aged >=18 years": 1,
        "Hearing disability among adults aged >=18 years": 1
    }

    # dict for shortening the Measures
    measure_replacements = {
        'All teeth lost among adults aged >=65 years': 'All teeth lost (>=65)',
        'Arthritis among adults aged >=18 years': 'Arthritis (>=18)',
        'Binge drinking among adults aged >=18 years': 'Binge drinking (>=18)',
        'Cancer (excluding skin cancer) among adults aged >=18 years': 'Cancer (>=18)',
        'Chronic kidney disease among adults aged >=18 years': 'Chronic kidney disease (>=18)',
        'Chronic obstructive pulmonary disease among adults aged >=18 years': 'COPD (>=18)',
        'Coronary heart disease among adults aged >=18 years': 'Coronary heart disease (>=18)',
        'Current asthma among adults aged >=18 years': 'Current asthma (>=18)',
        'Current lack of health insurance among adults aged 18-64 years': 'Lack of insurance (18-64)',
        'Current smoking among adults aged >=18 years': 'Current smoking (>=18)',
        'Depression among adults aged >=18 years': 'Depression (>=18)',
        'Diagnosed diabetes among adults aged >=18 years': 'Diagnosed diabetes (>=18)',
        'Fair or poor self-rated health status among adults aged >=18 years': 'Poor health self-rating (>=18)',
        'Mental health not good for >=14 days among adults aged >=18 years': 'Poor mental health (>=18)',
        'No cervical cancer screening among adult women aged 21-65 years': 'No cervical cancer screening (21-65)',
        'No colorectal cancer screening among adults aged 50-75 years': 'No colorectal cancer screening (50-75)',
        'No dental visit in past year among adults aged >=18 years': 'No dental visit (>=18)',
        'No doctor visit for checkup in past year among adults aged >=18 years': 'No doctor visit (>=18)',
        'No leisure-time physical activity among adults aged >=18 years': 'No physical activity (>=18)',
        'No mammography use among women aged 50-74 years': 'No mammography use (50-74)',
        'Obesity among adults aged >=18 years': 'Obesity (>=18)',
        'Older adult men aged >=65 years not up to date on clinical preventive services': 'Men not up to date: clinical preventive (>=65)',
        'Older adult women aged >=65 years not up to date on clinical preventive services': 'Women not up to date: clinical preventive (>=65)',
        'Physical health not good for >=14 days among adults aged >=18 years': 'Poor physical health (>=18)',
        'Sleeping less than 7 hours among adults aged >=18 years': 'Sleeping < 7 hours (>=18)',
        'Stroke among adults aged >=18 years': 'Stroke (>=18)',
        'Any disability among adults aged >=18 years':'Any disability (>=18)',
        'Cognitive disability among adults ages >=18 years':'Cognitive disability (>=18)',
        'Hearing disability among adults aged >=18 years': 'Hearing disability (>=18)',
        'Independent living disability among adults aged >=18 years':'Independent living disability (>=18)',
        'Mobility disability among adults aged >=18 years': 'Mobility disability (>=18)',
        'Self-care disability among adults aged >=18 years': 'Self-care disability (>=18)',
        'Vision disability among adults aged >=18 years': 'Vision disability (>=18)',
        'High blood pressure among adults aged >=18 years': 'High blood pressure (>=18)',
        'High cholesterol among adults aged >=18 years who have been screened in the past 5 years': 'High cholesterol if screening last 5 yrs (>=18)',
        'No cholesterol screening among adults aged >=18 years': 'No cholesterol screening (>=18)',
        'Not taking medicine for high blood pressure among adults aged >=18 years': 'Not on hypertension medicine (>=18)'
    }


    df = pd.read_pickle(CDC_filepath)
    df = df[df['LocationName'] != df['StateDesc']]  # Remove state data if any
    df = df.sort_values('Year', ascending=False).groupby(['GEOID', 'Measure']).first().reset_index()
    df.drop_duplicates(inplace=True)

    def normalize_within_group(df, column_name):
        min_val = df[column_name].min()
        max_val = df[column_name].max()
        df[column_name + '_Normalized'] = ((df[column_name] - min_val) / (max_val - min_val)) * 100
        return df
    
    # Assuming impact_scores is defined
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
