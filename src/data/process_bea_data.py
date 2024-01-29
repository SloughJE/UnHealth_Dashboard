import pandas as pd
import numpy as np

def process_bea_data(
                    bea_income_file="data/interim/df_BEA_income_1969_2023.pickle",
                    regional_cpi_file="data/interim/df_bls_regional_cpi_1969_2023.pickle", 
                    usa_cpi_file = "data/interim/df_bls_usa_cpi_1969_2023.pickle",
                    gpd_file = "data/interim/df_BEA_gdp_2017_2023.pickle"
                    ):

    regions_dict = {
        "West": ["WA", "OR", "ID", "MT", "WY", "CA", "NV", "UT", "CO", "AZ", "NM", "AK", "HI"],
        "Midwest": ["ND", "SD", "NE", "KS", "MN", "IA", "MO", "WI", "IL", "MI", "IN", "OH"],
        "South": ["TX", "OK", "AR", "LA", "MS", "AL", "GA", "FL", "SC", "NC", "VA", "WV", "KY", "TN", "DC", "MD", "DE"],
        "Northeast": ["PA", "NJ", "NY", "CT", "RI", "MA", "VT", "NH", "ME"]
    }


    df_bea_income = pd.read_pickle(bea_income_file)
    df_income = df_bea_income[df_bea_income.Statistic=='Per capita personal income']
    df_population = df_bea_income[df_bea_income.Statistic=='Population']

    df_regional_cpi = pd.read_pickle(regional_cpi_file)

    df_usa_cpi = pd.read_pickle(usa_cpi_file)
    df_usa_cpi.sort_values('year',inplace=True)

    # Extracting the state abbreviation from the GeoName column in df_income
    df_income['State'] = df_income['GeoName'].apply(lambda x: x.split(', ')[-1] if ', ' in x else None)
    # also do for population
    df_population['State'] = df_population['GeoName'].apply(lambda x: x.split(', ')[-1] if ', ' in x else None)

    # Creating a reverse mapping from state to region
    state_to_region = {state: region for region, states in regions_dict.items() for state in states}
    df_income['region'] = df_income['State'].map(state_to_region)

    # Renaming columns for merging
    df_usa_cpi.rename(columns={'year': 'TimePeriod', 'value': 'CPI'}, inplace=True)
    df_regional_cpi.rename(columns={'year': 'TimePeriod', 'value': 'CPI'}, inplace=True)

    # Merging the CPI data
    # For national data
    df_income_national = pd.merge(df_income[df_income['State'].isnull()], 
                                df_usa_cpi, 
                                on='TimePeriod', 
                                how='left')

    # For regional data
    df_income_regional = pd.merge(df_income[df_income['State'].notnull()], 
                                df_regional_cpi, 
                                on=['TimePeriod', 'region'], 
                                how='left')

    df_income_combined = pd.concat([df_income_national, df_income_regional])

    df_income_combined['DataValue'] = df_income_combined.DataValue.astype(int)
    df_income_combined['CPI'] = df_income_combined.CPI.astype(float)

    # add population back

    # Assuming the base year for CPI is 1982-84 and the index for that period is 100
    base_cpi = 100

    # Adjusting the 'DataValue' from df_income_combined to account for inflation
    # Create CPI adjusted income DataFrame
    df_adjusted_income = df_income_combined[['GeoFips', 'GeoName', 'TimePeriod', 'CL_UNIT', 'UNIT_MULT', 'State', 'region', 'CPI']].copy()
    df_adjusted_income['DataValue'] = (df_income_combined['DataValue'] / df_income_combined['CPI']) * base_cpi
    df_adjusted_income['Statistic'] = 'CPI Adjusted Per Capita Income'
    df_adjusted_income['UnitOfMeasure'] = '1982-84 CPI Dollars'

    # Concatenate with the original DataFrame
    df_income_combined = pd.concat([df_income_combined, df_adjusted_income])

    print(df_income_combined[df_income_combined.Statistic=='CPI Adjusted Per Capita Income'].head(2))
   
    df_income_combined = df_income_combined[['GeoFips','GeoName','TimePeriod','DataValue','Statistic','State']]
    print(df_income_combined.tail())

    ################################################
    # gdp data, calculate GDP per capita
    df_gdp = pd.read_pickle(gpd_file)
    df_gdp = df_gdp[(df_gdp.Statistic=='Real Gross Domestic Product (GDP)') | (df_gdp.Statistic=='Current-dollar Gross Domestic Product (GDP)')]


    # Split df_gdp into two separate DataFrames
    df_gdp_real = df_gdp[df_gdp.Statistic == 'Real Gross Domestic Product (GDP)']
    df_gdp_current = df_gdp[df_gdp.Statistic == 'Current-dollar Gross Domestic Product (GDP)']

    # Ensure DataValue is numeric in all DataFrames
    df_gdp_real['DataValue'] = pd.to_numeric(df_gdp_real['DataValue'], errors='coerce')
    df_gdp_current['DataValue'] = pd.to_numeric(df_gdp_current['DataValue'], errors='coerce')
    df_population['DataValue'] = pd.to_numeric(df_population['DataValue'], errors='coerce')

    # Filter df_bea for population data
    #df_bea_pop = df_bea[df_bea.Statistic == 'Population']

    # Function to calculate GDP per capita and return a formatted DataFrame
    def calculate_gdp_per_capita(df_gdp, gdp_statistic_name, df_population):
        df_merged = pd.merge(df_gdp, df_population, on=['GeoFips', 'GeoName', 'TimePeriod'], suffixes=('_gdp', '_population'))
        df_merged['GDP_per_capita'] = (df_merged['DataValue_gdp'] * 1000) / df_merged['DataValue_population']
        df_gdp_per_capita = df_merged[['GeoFips', 'GeoName', 'TimePeriod', 'GDP_per_capita']].copy()
        df_gdp_per_capita['Statistic'] = f'{gdp_statistic_name} Per Capita'
        df_gdp_per_capita['DataValue'] = df_gdp_per_capita['GDP_per_capita']
        df_gdp_per_capita['UnitOfMeasure'] = 'Dollars'
        df_gdp_per_capita.drop('GDP_per_capita', axis=1, inplace=True)
        return df_gdp_per_capita

    # Calculate GDP per capita for each GDP statistic
    df_gdp_per_capita_real = calculate_gdp_per_capita(df_gdp_real, 'Real GDP', df_population)
    df_gdp_per_capita_current = calculate_gdp_per_capita(df_gdp_current, 'Current-dollar GDP', df_population)

    # Combine all data into a single DataFrame
    df_combined = pd.concat([df_population, df_gdp_per_capita_real, df_gdp_per_capita_current])

    # Sort the DataFrame
    df_combined.sort_values(['GeoFips', 'TimePeriod', 'Statistic'], inplace=True)

    # Select relevant columns
    df_combined = df_combined[['GeoFips', 'GeoName', 'TimePeriod', 'Statistic', 'DataValue']]

    # Display the last few rows
    df_income_combined = pd.concat([df_income_combined, df_combined])
    print(df_combined.tail())

    fileout = "data/processed/bea_economic_data.pickle"
    df_income_combined.to_pickle(fileout)
    print(f"file saved to: {fileout}")