import json
import requests
import pandas as pd
import geopandas as gpd
from shapely import wkt


def get_cdc_places_data(
    link_2022_csv: str = "https://data.cdc.gov/api/views/duw2-7jbt/rows.csv?accessType=DOWNLOAD",
    link_2023_csv: str = "https://data.cdc.gov/api/views/swc5-untb/rows.csv?accessType=DOWNLOAD"
) -> None:
    """
    Downloads CDC PLACES data for the years 2022 and 2023, and saves it to a pickle file.

    Args:
        link_2022_csv (str): URL for the 2022 CDC PLACES data CSV.
        link_2023_csv (str): URL for the 2023 CDC PLACES data CSV.

    Returns:
        None: This function does not return any value but saves the concatenated data frame to a file.
    """
    print(f"Downloading CDC PLACES data from CDC for 2022 and 2023 release: {link_2022_csv} and {link_2023_csv}")

    # Downloading data for 2022 and 2023
    df_health_2022 = pd.read_csv(link_2022_csv)
    df_health_2023 = pd.read_csv(link_2023_csv)

    # Concatenating the dataframes
    df_health = pd.concat([df_health_2022, df_health_2023])

    # Defining output file path
    fileout = "data/raw/df_CDC_PLACES_raw.pickle"

    # Saving the dataframe to a pickle file
    df_health.to_pickle(fileout)

    print(f"Saved CDC PLACES data to: {fileout}")


def initial_processing_cdc_places_data(
    filepath_places: str = "data/raw/df_CDC_PLACES_raw.pickle",
    us_counties_geojson_url: str = 'https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip'
) -> None:
    """
    Performs initial processing on CDC PLACES data, including handling missing disability data for Florida,
    merging with US counties geolocation data, and adjusting measures for positive outcomes.

    Args:
        filepath_places (str): File path to the raw CDC PLACES data pickle file.
        us_counties_geojson_url (str): URL to download US counties GEOJSON data.

    Returns:
        None: This function does not return any value but saves the processed data to a file.
    """
    df_health = pd.read_pickle(filepath_places)

    # Handling missing disability data for Florida
    print("Dealing with Florida's lack of disability data")
    print("Inserting USA average for all Florida counties")
    
    # Extracting USA data for 'Disability' and 'Age-adjusted prevalence'
    usa_disability_data = df_health[
        (df_health.StateAbbr == 'US') & 
        (df_health.Category == 'Disability') & 
        (df_health.Data_Value_Type == 'Age-adjusted prevalence')
    ]

    # Extracting unique list of Florida counties with their Geolocation
    florida_counties_geo = df_health[df_health.StateAbbr == 'FL'][['LocationName', 'Geolocation']].drop_duplicates()

    # Replicating USA disability data for each Florida county, retaining the Geolocation
    florida_data_list = []
    for index, row in florida_counties_geo.iterrows():
        county_data = usa_disability_data.copy()
        county_data['LocationName'] = row['LocationName']
        county_data['StateAbbr'] = 'FL'
        county_data['StateDesc'] = 'Florida'
        county_data['Geolocation'] = row['Geolocation']
        florida_data_list.append(county_data)

    florida_data = pd.concat(florida_data_list, ignore_index=True)

    # Removing existing Florida disability data and appending new data
    df_health = df_health[~((df_health.StateAbbr == 'FL') & (df_health.Category == 'Disability'))]
    df_health = pd.concat([df_health, florida_data], ignore_index=True)
    print(f"Added this to data:{florida_data.head()}")

    df_health = df_health[df_health.Geolocation.notna()]
    df_health['Geolocation'] = df_health['Geolocation'].apply(wkt.loads)

    # Downloading US census geo data
    print(f"Downloading geolocation data from census: {us_counties_geojson_url}")
    us_counties = gpd.read_file(us_counties_geojson_url)
    us_counties_geojson = us_counties.to_json()
    us_counties_geojson_dict = json.loads(us_counties_geojson)

    # Saving the GeoJSON data to a file
    file_path_geo_json = "data/processed/us_census_counties_geojson.json"
    with open(file_path_geo_json, 'w') as f:
        json.dump(us_counties_geojson_dict, f)
    print(f"GeoJSON file saved to: {file_path_geo_json}")

    df_health = gpd.GeoDataFrame(df_health, geometry='Geolocation')
    print(f"Data shape before merge: {df_health.shape}")

    # Setting the CRS for the GeoDataFrame
    df_health.set_crs(epsg=4269, inplace=True)

    # Verifying CRS of GeoDataFrames
    print("CRS of df_health:", df_health.crs)
    print("CRS of us_counties:", us_counties.crs)

    # Merging CDC PLACES data with US counties geolocation data
    merged_gdf = gpd.sjoin(df_health, us_counties, how='left', predicate='intersects')
    print(f"Data shape after merge: {merged_gdf.shape}")

    # let's use only Age-adjusted prevalence
    #https://www.cdc.gov/nchs/hus/sources-definitions/age-adjustment.htm#:~:text=Age%2Dadjusted%20rates%20are%20computed,age%20differences%20in%20population%20composition.
    merged_gdf = merged_gdf[merged_gdf.Data_Value_Type != 'Crude prevalence']
    cols_wanted = ['Year', 'StateAbbr', 'StateDesc', 'LocationName', 'Category', 'Measure', 'Data_Value', 'Data_Value_Unit', 'GEOID', 'Geolocation']
    merged_gdf = merged_gdf[cols_wanted]
    
    
    # transform 'positive outcome' measures and values to inverse
    measure_mapping = {
        "Visits to doctor for routine checkup within the past year among adults aged >=18 years": "No doctor visit for checkup in past year among adults aged >=18 years",
        "Visits to dentist or dental clinic among adults aged >=18 years": "No dental visit in past year among adults aged >=18 years",
        "Fecal occult blood test, sigmoidoscopy, or colonoscopy among adults aged 50-75 years": "No colorectal cancer screening among adults aged 50-75 years",
        "Cervical cancer screening among adult women aged 21-65 years": "No cervical cancer screening among adult women aged 21-65 years",
        "Taking medicine for high blood pressure control among adults aged >=18 years with high blood pressure": "Not taking medicine for high blood pressure among adults aged >=18 years",
        "Cholesterol screening among adults aged >=18 years": "No cholesterol screening among adults aged >=18 years",
        "Mammography use among women aged 50-74 years": "No mammography use among women aged 50-74 years",
        "Older adult men aged >=65 years who are up to date on a core set of clinical preventive services: Flu shot past year, PPV shot ever, Colorectal cancer screening": "Older adult men aged >=65 years not up to date on clinical preventive services",
        "Older adult women aged >=65 years who are up to date on a core set of clinical preventive services: Flu shot past year, PPV shot ever, Colorectal cancer screening, and Mammogram past 2 years": "Older adult women aged >=65 years not up to date on clinical preventive services"
    }

    merged_gdf.rename(columns={'Measure': 'Original_Measure'}, inplace=True)

    merged_gdf['Measure'] = merged_gdf['Original_Measure'].apply(lambda x: measure_mapping.get(x, x))
    # Invert data values for positive measures
    merged_gdf['Data_Value'] = merged_gdf.apply(lambda row: 100 - row['Data_Value'] if row['Measure'] in measure_mapping.values() else row['Data_Value'], axis=1)

    output_filepath = "data/interim/CDC_PLACES_GEOID.pickle"
    merged_gdf.to_pickle(output_filepath)
    print(f"file saved to: {output_filepath}")


##########################################
# FROM USA SPENDING, Currently not used###
##########################################
def get_spending_data(year_wanted: int) -> None:
    """
    Fetches and saves spending data by county for a specified fiscal year from the USA Spending API.

    Note: This function is not currently used in this project.

    Args:
        year_wanted (int): The fiscal year for which spending data is requested.

    Returns:
        None: This function does not return any value but saves the fetched data to a pickle file.
    """
    import requests
    import pandas as pd
    import us

    def fetch_spending_data_by_county(fiscal_year: int) -> pd.DataFrame:
        """
        Fetches spending data by county for a specified fiscal year.

        Args:
            fiscal_year (int): The fiscal year for which spending data is requested.

        Returns:
            pd.DataFrame: A DataFrame containing the spending data for the requested fiscal year.
        """
        url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "scope": "place_of_performance",
            "geo_layer": "county",
            "filters": {
                "time_period": [{"start_date": f"{fiscal_year}-01-01", "end_date": f"{fiscal_year}-12-31"}]
            }
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print("Request successful")
            response_json = response.json()
            results = response_json['results']

            for result in results:
                fips_code = result['shape_code']
                state = us.states.lookup(fips_code[:2])
                result['state_code'] = state.abbr if state else None

            df = pd.DataFrame(results)
            df['fiscal_year'] = fiscal_year
            return df
        else:
            print("Request failed")
            print(response.status_code)
            print(response.text)
            return pd.DataFrame()

    print(f"Pulling data from USA Spending API for {year_wanted}")
    df_spending = fetch_spending_data_by_county(year_wanted)
    print(df_spending)
    fileout = f"data/interim/USA_Spending_{year_wanted}.pickle"
    df_spending.to_pickle(fileout)
    print(f"Spending data saved to: {fileout}")

#################
## BEA DATA #####
#################

    
def get_bea_income_data(
    api_key: str,
    table_name: str = 'CAINC1',
    year_min: int = 1969,
    year_max: int = 2023,
    line_codes: list[str] = ['1', '2', '3']
) -> None:
    """
    Fetches and saves BEA income data for a specified range of years and line codes, for both counties and states.

    Args:
        api_key (str): The API key required for the BEA data API.
        table_name (str): The name of the table from which to fetch the data. Defaults to 'CAINC1'.
        year_min (int): The starting year for the data fetch. Defaults to 1969.
        year_max (int): The ending year for the data fetch. Defaults to 2023.
        line_codes (list[str]): The line codes specifying the types of income data to fetch. Defaults to ['1', '2', '3'].

    Returns:
        None: This function does not return any value but saves the fetched data to a pickle file.
    """
    years = [str(year) for year in range(year_min, year_max)]
    year_range = ','.join(years)

    dfs = []  # DataFrames list
    statistics = []  # Statistic descriptions list
    unit_of_measures = []  # Unit of measures descriptions list

    # Fetching county data
    print("Getting county data")
    for line_code in line_codes:
        url = f"https://apps.bea.gov/api/data/?UserID={api_key}&method=GetData&datasetname=Regional&TableName={table_name}&LineCode={line_code}&Year={year_range}&GeoFips=COUNTY&ResultFormat=json"
        response = requests.get(url)
        data = response.json()
        statistic = data['BEAAPI']['Results']['Statistic']
        unit_of_measure = data['BEAAPI']['Results']['UnitOfMeasure']

        statistics.append(statistic)
        unit_of_measures.append(unit_of_measure)

        data_list = data['BEAAPI']['Results']['Data']
        df = pd.DataFrame(data_list)
        dfs.append(df)

    # Adding 'Statistic' and 'UnitOfMeasure' to each DataFrame
    for i, df in enumerate(dfs):
        df['Statistic'] = statistics[i]
        df['UnitOfMeasure'] = unit_of_measures[i]

    county_df = pd.concat(dfs, ignore_index=True)
    print(f"County data shape: {county_df.shape}")
    print(f"Number of unique GeoFips in county data: {county_df.GeoFips.nunique()}")

    # Resetting lists for state and USA totals fetching
    dfs = []  # DataFrames list
    statistics = []  # Statistic descriptions list
    unit_of_measures = []  # Unit of measures descriptions list

    # Fetching state and country data
    print("Getting state and country data")
    for line_code in line_codes:
        url = f"https://apps.bea.gov/api/data/?UserID={api_key}&method=GetData&datasetname=Regional&TableName={table_name}&LineCode={line_code}&Year={year_range}&GeoFips=STATE&ResultFormat=json"
        response = requests.get(url)
        data = response.json()

        statistic = data['BEAAPI']['Results']['Statistic']
        unit_of_measure = data['BEAAPI']['Results']['UnitOfMeasure']

        statistics.append(statistic)
        unit_of_measures.append(unit_of_measure)

        data_list = data['BEAAPI']['Results']['Data']
        df = pd.DataFrame(data_list)
        dfs.append(df)

    # Adding 'Statistic' and 'UnitOfMeasure' to each DataFrame
    for i, df in enumerate(dfs):
        df['Statistic'] = statistics[i]
        df['UnitOfMeasure'] = unit_of_measures[i]

    state_country_df = pd.concat(dfs, ignore_index=True)
    print(f"State and country data shape: {state_country_df.shape}")
    print(f"Number of unique GeoFips in state and country data: {state_country_df.GeoFips.nunique()}")

    df_income = pd.concat([county_df, state_country_df], ignore_index=True)
    print(df_income.head(2))
    print(df_income.tail(2))
    print(f"Combined data shape: {df_income.shape}")
    print(f"Number of unique GeoFips in combined data: {df_income.GeoFips.nunique()}")

    file_out = f"data/interim/df_BEA_income_{year_min}_{year_max}.pickle"
    df_income.to_pickle(file_out)
    print(f"File saved to: {file_out}")


def get_bea_gdp_data(
    api_key: str,
    table_name: str = 'CAGDP1',
    year_min: int = 2017,
    year_max: int = 2023,
    line_codes: list[str] = ['1', '2', '3']
) -> None:
    """
    Fetches and saves BEA GDP data by county, state, and country for a specified range of years and line codes.

    Args:
        api_key (str): The API key required for the BEA data API.
        table_name (str): The name of the table from which to fetch the GDP data. Defaults to 'CAGDP1'.
        year_min (int): The starting year for the data fetch. Defaults to 2017.
        year_max (int): The ending year for the data fetch. Defaults to 2023.
        line_codes (list[str]): The line codes specifying the types of GDP data to fetch. Defaults to ['1', '2', '3'].

    Returns:
        None: This function does not return any value but saves the fetched data to a pickle file.
    """
    years = [str(year) for year in range(year_min, year_max)]
    year_range = ','.join(years)

    dfs = []  # List to hold DataFrames of fetched data
    statistics = []  # List to hold statistics descriptions

    # Fetching county data
    print("Getting county data")
    for line_code in line_codes:
        url = f"https://apps.bea.gov/api/data/?UserID={api_key}&method=GetData&datasetname=Regional&TableName={table_name}&LineCode={line_code}&Year={year_range}&GeoFips=COUNTY&ResultFormat=json"
        response = requests.get(url)
        data = response.json()
        statistic = data['BEAAPI']['Results']['Statistic']

        statistics.append(statistic)

        data_list = data['BEAAPI']['Results']['Data']
        df = pd.DataFrame(data_list)
        dfs.append(df)

    # Adding 'Statistic' to each DataFrame
    for i, df in enumerate(dfs):
        df['Statistic'] = statistics[i]

    county_df = pd.concat(dfs, ignore_index=True)
    print(f"County data shape: {county_df.shape}")
    print(f"Number of unique GeoFips in county data: {county_df.GeoFips.nunique()}")

    # Resetting lists for fetching state and USA totals
    dfs = []  # List to hold DataFrames
    statistics = []  # List to hold statistics descriptions

    # Fetching state and country data
    print("Getting state and country data")
    for line_code in line_codes:
        url = f"https://apps.bea.gov/api/data/?UserID={api_key}&method=GetData&datasetname=Regional&TableName={table_name}&LineCode={line_code}&Year={year_range}&GeoFips=STATE&ResultFormat=json"
        response = requests.get(url)
        data = response.json()

        statistic = data['BEAAPI']['Results']['Statistic']
        statistics.append(statistic)

        data_list = data['BEAAPI']['Results']['Data']
        df = pd.DataFrame(data_list)
        dfs.append(df)

    # Adding 'Statistic' to each DataFrame
    for i, df in enumerate(dfs):
        df['Statistic'] = statistics[i]

    state_country_df = pd.concat(dfs, ignore_index=True)
    print(f"State and country data shape: {state_country_df.shape}")
    print(f"Number of unique GeoFips in state and country data: {state_country_df.GeoFips.nunique()}")

    df_gdp = pd.concat([county_df, state_country_df], ignore_index=True)
    print(df_gdp.head(2))
    print(df_gdp.tail(2))
    print(f"Combined data shape: {df_gdp.shape}")
    print(f"Number of unique GeoFips in combined data: {df_gdp.GeoFips.nunique()}")

    file_out = f"data/interim/df_BEA_gdp_{year_min}_{year_max}.pickle"
    df_gdp.to_pickle(file_out)
    print(f"File saved to: {file_out}")


##################
## BLS CPI DATA ##
##################
# found looking at: https://www.bls.gov/cpi/regional-resources.htm
# documentation regarding the series is lacking
    
def get_regional_bls_cpi_data(api_key: str, start_year: int, end_year: int) -> None:
    """
    Fetches and saves regional Consumer Price Index (CPI) data from the Bureau of Labor Statistics (BLS) API
    for specified years and regions.

    Args:
        api_key (str): The API key required for accessing the BLS data API.
        start_year (int): The starting year for the data fetch.
        end_year (int): The ending year for the data fetch.

    Returns:
        None: This function does not return any value but saves the fetched data to a pickle file.
    """
    print(f"Pulling regional CPI data from {start_year} to {end_year}")

    def generate_year_ranges(start: int, end: int, interval: int = 20) -> list:
        """
        Generates a list of year ranges, each spanning up to 'interval' years, from 'start' to 'end'.

        Args:
            start (int): The start year.
            end (int): The end year.
            interval (int): The number of years each range should cover.

        Returns:
            list: A list of tuples, each representing a start and end year for a range.
        """
        return [(year, min(year + interval - 1, end)) for year in range(start, end, interval)]

    # Series IDs for different regions, as found on the BLS website
    bls_series_dict = {
        "South": ["CUUR0300SA0", "CUUS0300SA0"],
        "West": ["CUUR0400SA0", "CUUS0400SA0"],
        "Midwest": ["CUUR0200SA0", "CUUS0200SA0"],
        "NorthEast": ["CUUR0100SA0", "CUUS0100SA0"]
    }

    headers = {'Content-type': 'application/json'}
    all_data = []

    for region, series_ids in bls_series_dict.items():
        for start_year_loop, end_year_loop in generate_year_ranges(start_year, end_year):
            data = json.dumps({
                "seriesid": series_ids,
                "startyear": str(start_year_loop),
                "endyear": str(end_year_loop),
                "annualaverage": True,
                "registrationkey": api_key
            })

            response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
            cpi_data = response.json()

            if cpi_data.get('Results', {}):
                for i, series_id in enumerate(series_ids):
                    series_data = cpi_data['Results']['series'][i]['data']
                    annual_data = [item for item in series_data if item['periodName'] == 'Annual']
                    for item in annual_data:
                        item['region'] = region
                        all_data.append(item)
            else:
                print(f"No data for series {series_ids} in region {region} for years {start_year_loop}-{end_year_loop}")

    # Organizing the DataFrame
    df = pd.DataFrame(all_data)
    df = df[['year', 'value', 'region']]
    df = df.sort_values(by=['region', 'year'])
    df.drop_duplicates(inplace=True)

    print(df.head(2))
    print(df.tail(2))
    print(f"DataFrame shape: {df.shape}")
    region_counts = df.groupby('region').count()
    print(region_counts)

    file_out = f"data/interim/df_bls_regional_cpi_{start_year}_{end_year}.pickle"
    df.to_pickle(file_out)
    print(f"File saved to: {file_out}")


#  USA CPI  
def get_usa_bls_cpi_data(api_key: str, start_year: int, end_year: int) -> None:
    """
    Fetches and saves the USA Consumer Price Index (CPI) data from the Bureau of Labor Statistics (BLS) API
    for a specified range of years.

    Args:
        api_key (str): The API key required for accessing the BLS data API.
        start_year (int): The starting year for the data fetch.
        end_year (int): The ending year for the data fetch.

    Returns:
        None: This function does not return any value but saves the fetched data to a pickle file.
    """
    print(f"Pulling USA CPI data from {start_year} to {end_year}")

    def generate_year_ranges(start: int, end: int, interval: int = 20) -> list:
        """
        Generates a list of year ranges, each spanning up to 'interval' years, from 'start' to 'end'.

        Args:
            start (int): The start year.
            end (int): The end year.
            interval (int): The number of years each range should cover.

        Returns:
            list: A list of tuples, each representing a start and end year for a range.
        """
        return [(year, min(year + interval - 1, end)) for year in range(start, end, interval)]

    headers = {'Content-type': 'application/json'}
    all_data = []

    for start_year_loop, end_year_loop in generate_year_ranges(start_year, end_year):
        data = json.dumps({
            "seriesid": ["CUUR0000SA0"],
            "startyear": str(start_year_loop),
            "endyear": str(end_year_loop),
            "annualaverage": True,
            "registrationkey": api_key
        })

        response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
        cpi_data = response.json()

        if 'Results' in cpi_data and 'series' in cpi_data['Results']:
            series_data = cpi_data['Results']['series'][0]['data']
            annual_data = [item for item in series_data if item['periodName'] == 'Annual']
            all_data.extend(annual_data)
        else:
            print(f"No data for series CUUR0000SA0 in USA for years {start_year_loop}-{end_year_loop}")

    # Organizing the DataFrame
    df = pd.DataFrame(all_data)
    df = df[['year', 'value']]
    df['value'] = df['value'].astype(float)  # Ensuring 'value' column is float for analysis
    df.drop_duplicates(subset=['year'], inplace=True)  # Removing duplicate years

    print(df.head(2))
    print(df.tail(2))
    print(f"DataFrame shape: {df.shape}")
    print(f"Data from year: {df.year.min()} to {df.year.max()}")

    file_out = f"data/interim/df_bls_usa_cpi_{start_year}_{end_year}.pickle"
    df.to_pickle(file_out)
    print(f"File saved to: {file_out}")

    
def get_state_census_geo_file(us_census_state_geojson_url: str = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_state_20m.zip") -> None:
    """
    Downloads state geolocation data from the US Census website, converts it to GeoJSON format, 
    and saves it to a file.

    Args:
        us_census_state_geojson_url (str): The URL to download the US state geolocation data in zip format. 
        Defaults to the 2021 shapefile for US states at a 1:20,000,000 scale.

    Returns:
        None: This function does not return any value but writes the geolocation data to a GeoJSON file.
    """
    print(f"Downloading geolocation data from census: {us_census_state_geojson_url}")
    us_states = gpd.read_file(us_census_state_geojson_url)
    # Convert GeoDataFrame to JSON string and then to a Python dictionary
    us_states_geojson = us_states.to_json()
    us_states_geojson_dict = json.loads(us_states_geojson)

    # Write the dictionary to a file in JSON format
    file_path_geo_json = "data/interim/us_census_state_geojson.json"
    with open(file_path_geo_json, 'w') as f:
        json.dump(us_states_geojson_dict, f)
    print(f"GeoJSON file saved to: {file_path_geo_json}")