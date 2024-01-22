import os
import json

import pandas as pd
import geopandas as gpd
from shapely import wkt

def load_process_CDC_PLACES_data(save_og_files):


    link_2022_csv = "https://data.cdc.gov/api/views/duw2-7jbt/rows.csv?accessType=DOWNLOAD" # actual link to 2022 release download
    link_2023_csv = "https://data.cdc.gov/api/views/swc5-untb/rows.csv?accessType=DOWNLOAD" # actual link to 2023 release download
    print(f"downloading CDC LOCALS data from CDC for 2022 and 2023 release: {link_2022_csv} and {link_2023_csv}")

    df_health_2022 = pd.read_csv(link_2022_csv)
    df_health_2023 = pd.read_csv(link_2023_csv)

    if save_og_files:

        raw_output_dir = "data/raw/"
        filepath_2022 = os.path.join(raw_output_dir,'CDC_PLACES_2022.pickle')
        filepath_2023 = os.path.join(raw_output_dir,'CDC_PLACES_2023.pickle')

        df_health_2022.to_pickle(filepath_2022)
        df_health_2023.to_pickle(filepath_2023)
        print(f"OG files saved to: {filepath_2022} and {filepath_2023}")

    df_health = pd.concat([df_health_2022,df_health_2023])
    df_health = df_health[df_health.Geolocation.notna()] # this would remove USA total or avg
    df_health['Geolocation'] = df_health['Geolocation'].apply(wkt.loads) # Convert the 'Geolocation' column to a GeoSeries

    
    us_counties_geojson_url = 'https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip'
    print(f"downloading geolocation data from census: {us_counties_geojson_url}")
    us_counties = gpd.read_file(us_counties_geojson_url)
    # Convert GeoDataFrame to JSON string and then to a Python dictionary
    us_counties_geojson = us_counties.to_json()
    us_counties_geojson_dict = json.loads(us_counties_geojson)

    # Write the dictionary to a file in JSON format
    file_path_geo_json = "data/interim/us_census_counties_geojson.json"
    with open(file_path_geo_json, 'w') as f:
        json.dump(us_counties_geojson_dict, f)
    print(f"GeoJSON file saved to: {file_path_geo_json}")

    df_health = gpd.GeoDataFrame(df_health, geometry='Geolocation')
    print(f"data shape before merge: {df_health.shape}")

    # Set the CRS of gdf_health to NAD83 (EPSG:4269)
    df_health.set_crs(epsg=4269, inplace=True)

    # Verify the CRS of both GeoDataFrames
    print("CRS of gdf_health:", df_health.crs)
    print("CRS of us_counties:", us_counties.crs)

    merged_gdf = gpd.sjoin(df_health, us_counties, how='left', predicate='intersects')
    print(f"data shape after merge: {merged_gdf.shape}")

    # let's use only Age-adjusted prevalence
    #https://www.cdc.gov/nchs/hus/sources-definitions/age-adjustment.htm#:~:text=Age%2Dadjusted%20rates%20are%20computed,age%20differences%20in%20population%20composition.
    merged_gdf = merged_gdf[merged_gdf.Data_Value_Type!='Crude prevalence']

    cols_wanted = ['Year','StateAbbr','StateDesc','LocationName','Measure','Data_Value','Data_Value_Unit','GEOID','Geolocation']
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

    # Apply the mapping to the DataFrame
    merged_gdf['Measure'] = merged_gdf['Measure'].apply(lambda x: measure_mapping.get(x, x))
    # Invert data values for positive measures
    merged_gdf['Data_Value'] = merged_gdf.apply(lambda row: 100 - row['Data_Value'] if row['Measure'] in measure_mapping.values() else row['Data_Value'], axis=1)

    output_filepath = "data/interim/CDC_PLACES_GEOID.pickle"
    merged_gdf.to_pickle(output_filepath)
    print(f"file saved to: {output_filepath}")


def rank_counties_by_year(CDC_filepath):
    
    impact_scores = {
        "Stroke among adults aged >=18 years": 5,
        "Chronic obstructive pulmonary disease among adults aged >=18 years": 5,
        "Cancer (excluding skin cancer) among adults aged >=18 years": 5,
        "Diagnosed diabetes among adults aged >=18 years": 5,
        "Coronary heart disease among adults aged >=18 years": 5,
        "Chronic kidney disease among adults aged >=18 years": 5,
        "Cognitive disability among adults ages >=18 years": 5,

        "Current smoking among adults aged >=18 years": 4,
        "Obesity among adults aged >=18 years": 4,
        "Depression among adults aged >=18 years": 4,
        "Binge drinking among adults aged >=18 years": 4,
        "Mental health not good for >=14 days among adults aged >=18 years": 4,
        "Mobility disability among adults aged >=18 years": 4,
        "High blood pressure among adults aged >=18 years": 4,

        "Arthritis among adults aged >=18 years": 3,
        "No leisure-time physical activity among adults aged >=18 years": 3,
        "Vision disability among adults aged >=18 years": 3,
        "Any disability among adults aged >=18 years": 3,
        "Physical health not good for >=14 days among adults aged >=18 years": 3,
        "Fair or poor self-rated health status among adults aged >=18 years": 3,

        
        "High cholesterol among adults aged >=18 years who have been screened in the past 5 years": 2,
        "Sleeping less than 7 hours among adults aged >=18 years": 2,
        "Current asthma among adults aged >=18 years": 2,
        "All teeth lost among adults aged >=65 years": 2,
        "Independent living disability among adults aged >=18 years": 2,
        "Not taking medicine for high blood pressure among adults aged >=18 years": 2,
        "Current lack of health insurance among adults aged 18-64 years": 2,
        "Older adult men aged >=65 years not up to date on clinical preventive services": 2,
        "Older adult women aged >=65 years not up to date on clinical preventive services": 2,
        "Self-care disability among adults aged >=18 years": 2,

        "No mammography use among women aged 50-74 years": 1,
        "No colorectal cancer screening among adults aged 50-75 years": 1,
        "No cervical cancer screening among adult women aged 21-65 years": 1,
        "No doctor visit for checkup in past year among adults aged >=18 years": 1,
        "No dental visit in past year among adults aged >=18 years": 1,
        "No cholesterol screening among adults aged >=18 years": 1,
        "Hearing disability among adults aged >=18 years": 1
    }

    df = pd.read_pickle(CDC_filepath)
    df = df[df['LocationName'] != df['StateDesc']] # remove state data if any

    def invert_normalize_within_group(df, column_name):
        min_val = df[column_name].min()
        max_val = df[column_name].max()
        df[column_name + '_Inverted_Normalized'] = 100 - ((df[column_name] - min_val) / (max_val - min_val)) * 100
        return df

    df = df.groupby(['Year', 'Measure']).apply(lambda x: invert_normalize_within_group(x, 'Data_Value')).reset_index(drop=True)

    df['Weighted_Score'] = df.apply(lambda row: row['Data_Value_Inverted_Normalized'] * impact_scores.get(row['Measure'], 0), axis=1)

    county_year_scores = df.groupby(['Year', 'GEOID', 'LocationName', 'StateDesc', 'StateAbbr'])['Weighted_Score'].sum().reset_index()

    def normalize_within_year_group(df, column_name):
        min_val = df[column_name].min()
        max_val = df[column_name].max()
        df[column_name + '_Normalized'] = ((df[column_name] - min_val) / (max_val - min_val)) * 100
        return df

    county_year_scores = county_year_scores.groupby('Year').apply(lambda x: normalize_within_year_group(x, 'Weighted_Score')).reset_index(drop=True)
    # Add a ranking column within each year based on the normalized weighted score
    # method='min' assigns same rank to ties
    # Rank the scores, higher is now better
    county_year_scores['Rank'] = county_year_scores.groupby('Year')['Weighted_Score_Normalized'].rank(ascending=False, method='min')
    county_year_scores['Rank'] = county_year_scores['Rank'].astype(int)
    county_year_scores = county_year_scores.sort_values(by=['Year', 'Rank'])

    print(county_year_scores[county_year_scores.Year==2020])
    output_filepath = "data/interim/CDC_PLACES_county_rankings_by_year.pickle"
    county_year_scores.to_pickle(output_filepath)
    print(f"file saved to: {output_filepath}")


####################################
# FROM USA SPENDING
def get_spending_data(year_wanted):
    import requests
    import pandas as pd
    import us

    def fetch_spending_data_by_county(fiscal_year):
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
    print(f"Spending data saved to: {fileout}")

    df_spending.to_pickle(fileout)

##################
# FROM BEA
# Read the CSV file, skipping the first 3 rows and the last 11 rows
def process_gdp_data(filepath_in,filepath_out):

    df_gdp = pd.read_csv(filepath_in, skiprows=3, skipfooter=11, engine='python')

    # Rename the columns
    df_gdp.columns = ['GeoFips', 'GeoName', 'gdp_thousands']

    # Convert 'gdp_thousands' to numeric, coercing errors to NaN
    df_gdp['gdp_thousands'] = pd.to_numeric(df_gdp['gdp_thousands'], errors='coerce')

    # Multiply by 1000 to convert to actual GDP
    df_gdp['gdp'] = df_gdp['gdp_thousands'] * 1000
    df_gdp['GeoFips'] = df_gdp.GeoFips.astype(str)
    df_gdp.to_pickle(filepath_out)
    print(df_gdp)
    print(f"data processed and saved to{filepath_out}")

    
