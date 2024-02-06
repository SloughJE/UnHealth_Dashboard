import pandas as pd


def check_fips_county_data_ranking(df_bea, df_ranking):
    # map full state name to abbr
    state_mapping = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
            "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
            "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
            "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
            "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
            "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
            "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
            "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
            "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
            "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
        }
    
    # Add columns for matched_GEOID and Note to df_ranking
    df_ranking['matched_GEOID'] = df_ranking['GEOID']
    df_ranking['Note'] = ''

    # Process each row in df_ranking
    for index, row in df_ranking.iterrows():
        fips_county = row['GEOID']
        selected_state = row['StateDesc']
        selected_county = row['LocationName']

        # Check if FIPS code exists in the dataset
        if len(df_bea[df_bea.GeoFips == fips_county]) == 0:
            selected_state_abbr = state_mapping[selected_state]
            # Filter by selected state
            df_bea_find_fips = df_bea[df_bea.State == selected_state_abbr]
            
            # Try finding the county using the full selected_county name
            matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(selected_county, case=False, na=False)]
            
            # If not found, split the selected_county and try with the first part
            if matching_rows.empty and ' ' in selected_county:
                first_part_of_county = selected_county.split(' ')[0]
                matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(first_part_of_county, case=False, na=False)]
            
            # Update matched_GEOID if a match is found
            if not matching_rows.empty:
                df_ranking.at[index, 'matched_GEOID'] = matching_rows.GeoFips.iloc[0]
                df_ranking.at[index, 'Note'] = f"Econ data from {matching_rows.GeoName.iloc[0]}"


def create_final_summary_df(df_ranking_path="data/processed/CDC_PLACES_county_rankings.pickle", 
                            df_bea_path="data/processed/bea_economic_data.pickle", 
                            bea_year=2022,
                            fileout_path="data/processed/df_summary_final.pickle"):

    ### Load data#####
    df_ranking = pd.read_pickle(df_ranking_path)

    df_bea = pd.read_pickle(df_bea_path)
    df_bea = df_bea[(df_bea.TimePeriod==bea_year) & (df_bea.State.notnull()) & ((df_bea.Statistic=='Population') | (df_bea.Statistic=='Per capita personal income'))]

    ############
    check_fips_county_data_ranking(df_bea, df_ranking)
    # Extract necessary columns from df_bea
    df_bea_pivot = df_bea.pivot(index='GeoFips', columns='Statistic', values='DataValue')

    # Merge the DataFrames
    # Assuming df_bea_pivot has GeoFips as an index
    df = pd.merge(df_ranking, df_bea_pivot, left_on='matched_GEOID', right_index=True, how='left')
    df = df[['GEOID','LocationName','StateDesc','StateAbbr','Weighted_Score_Normalized', 'Rank','Population','Per capita personal income','Note']]
    df.to_pickle(fileout_path)
    print(df.head(2))
    print(f"file saved to: {fileout_path}")


def create_final_measures_df(
        df_measures_path="data/processed/CDC_PLACES_county_measures.pickle",
        fileout_path="data/processed/df_measures_final.pickle"
        ):
    ### Load data#####
    df_measures = pd.read_pickle(df_measures_path)
    df_measures = df_measures[['GEOID','Year','StateDesc','LocationName','Category','Data_Value', 'Measure_short','absolute_contribution']]
    df_measures['County Measure Rank'] = df_measures.groupby('Measure_short')['Data_Value'].rank(ascending=True, method='min')
    df_measures['Data_Value'] = df_measures['Data_Value']/100

    ############
    # currently not adding any income data to this df. Map is only for CDC Measures, not adding econ
    ############
    #df_bea = pd.read_pickle(df_bea_path)
    #df_bea = df_bea[(df_bea.TimePeriod==bea_year) & (df_bea.State.notnull()) & ((df_bea.Statistic=='Population') | (df_bea.Statistic=='Per capita personal income'))]
    
    def check_fips_county_data(df_bea, df_measures):
        # map full state name to abbr
        state_mapping = {
                "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
                "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
                "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
                "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
                "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
                "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
                "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
                "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
                "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
            }
        
        # Add columns for matched_GEOID and Note to df_measures
        df_measures['matched_GEOID'] = df_measures['GEOID']
        df_measures['Note'] = ''

        # Process each row in df_measures
        for index, row in df_measures.iterrows():
            fips_county = row['GEOID']
            selected_state = row['StateDesc']
            selected_county = row['LocationName']

            # Check if FIPS code exists in the dataset
            if len(df_bea[df_bea.GeoFips == fips_county]) == 0:
                selected_state_abbr = state_mapping[selected_state]
                # Filter by selected state
                df_bea_find_fips = df_bea[df_bea.State == selected_state_abbr]
                
                # Try finding the county using the full selected_county name
                matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(selected_county, case=False, na=False)]
                
                # If not found, split the selected_county and try with the first part
                if matching_rows.empty and ' ' in selected_county:
                    first_part_of_county = selected_county.split(' ')[0]
                    matching_rows = df_bea_find_fips[df_bea_find_fips.GeoName.str.contains(first_part_of_county, case=False, na=False)]
                
                # Update matched_GEOID if a match is found
                if not matching_rows.empty:
                    df_measures.at[index, 'matched_GEOID'] = matching_rows.GeoFips.iloc[0]
                    df_measures.at[index, 'Note'] = f"Econ data from {matching_rows.GeoName.iloc[0]}"


    df_measures.to_pickle(fileout_path)
    df_measures.to_pickle(fileout_path)
    print(df_measures.head(2))
    print(f"file saved to: {fileout_path}")