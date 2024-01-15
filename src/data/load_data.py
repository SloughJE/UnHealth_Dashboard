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

    cols_wanted = ['Year','StateAbbr','StateDesc','LocationName','Measure','Data_Value','Data_Value_Unit','GEOID']
    merged_gdf = merged_gdf[cols_wanted]
    output_filepath = "data/interim/CDC_PLACES_GEOID.pickle"
    merged_gdf.to_pickle(output_filepath)
    print(f"file saved to: {output_filepath}")