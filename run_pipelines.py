import sys 
import argparse
#from dotenv import load_dotenv

from src.data.load_data import (get_CDC_PLACES_data, initial_processing_CDC_PLACES_data, process_gdp_data, get_spending_data, 
                                get_bea_income_data, get_bea_gdp_data, get_regional_bls_cpi_data, get_usa_bls_cpi_data,
                                get_state_census_geo_file)
from src.data.merge_data import merge_gdp_ranking_data
from src.data.process_CDC_data import process_cdc_data
from src.data.process_bea_data import process_bea_data
from src.data.create_final_datasets import create_final_summary_df, create_final_measures_df
from src.models.gam_model import fit_gam


#load_dotenv()
# Load environment variables from .env file
#bea_api_key = os.getenv("bea_api_key")
#bls_api_key = os.getenv("bls_api_key")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--get_CDC_PLACES_data",
        help="load and process raw data from CDC",
        action="store_true"
    )
    parser.add_argument(
        "--initial_processing_CDC_PLACES_data",
        help="fix Florida and geo merge",
        action="store_true"
    )

    parser.add_argument(
        "--process_cdc_data",
        help="create a subjective ranking of counties",
        action="store_true"
    )

    parser.add_argument(
        "--process_gdp",
        help="make features",
        action="store_true"
    )

    parser.add_argument(
        "--get_spending",
        help="spending data from USA Spending API",
        action="store_true"
    )

    parser.add_argument(
        "--merge_ranking_gdp_spending",
        help="make features",
        action="store_true"
    )

    parser.add_argument(
        "--get_bea_income_data",
        help="get income per county, state and country from BEA api",
        action="store_true"
    )

    parser.add_argument(
        "--get_bea_gdp_data",
        help="get gdp per county, state and country from BEA api",
        action="store_true"
    )

    parser.add_argument(
        "--get_bls_regional_cpi",
        help="get regional CPI from BLS api",
        action="store_true"
    )
    
    parser.add_argument(
        "--get_bls_usa_cpi",
        help="get USA CPI from BLS api",
        action="store_true"
    )

    parser.add_argument(
        "--get_state_census_geodata",
        help="get USA state geodata from Census",
        action="store_true"
    )

    parser.add_argument(
        "--process_bea_data",
        help="process and adjust income data by regional CPI",
        action="store_true"
    )

    parser.add_argument(
        "--create_final_summary_dataset",
        help="create final summary df from BEA and df_ranking data",
        action="store_true"
    )

    parser.add_argument(
        "--create_final_measures_dataset",
        help="create final measures df from full measures df",
        action="store_true"
    )

    parser.add_argument(
        "--fit_gam",
        help="fit GAM to final dataset",
        action="store_true"
    )


    args = parser.parse_args()

    if len(sys.argv) == 1:
        print("No arguments, please add arguments")
    else:
  
        if args.get_CDC_PLACES_data:
            get_CDC_PLACES_data(
                link_2022_csv = "https://data.cdc.gov/api/views/duw2-7jbt/rows.csv?accessType=DOWNLOAD",
                link_2023_csv = "https://data.cdc.gov/api/views/swc5-untb/rows.csv?accessType=DOWNLOAD"
            )

        if args.initial_processing_CDC_PLACES_data:
            initial_processing_CDC_PLACES_data(
                filepath_PLACES="data/raw/df_CDC_PLACES_raw.pickle",
                us_counties_geojson_url = 'https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip'
            )

        if args.process_cdc_data:
            process_cdc_data(CDC_filepath="data/interim/CDC_PLACES_GEOID.pickle")

        if args.process_gdp:
            process_gdp_data(
                filepath_in="data/raw/BEA/county_gdp_fips_2020.csv",
                filepath_out="data/interim/county_gdp_fips_2020.pickle"
                )

        if args.get_spending:
            get_spending_data(2020)

        if args.merge_ranking_gdp_spending:
            merge_gdp_ranking_data(
                year=2020,
                gdp_filepath = "data/interim/county_gdp_fips_2020.pickle",
                ranking_filepath = "data/interim/CDC_PLACES_county_rankings_by_year.pickle",
                spending_filepath = "data/interim/USA_Spending_2020.pickle"

            )

        if args.get_bea_income_data:
            get_bea_income_data(
                bea_api_key,
                table_name='CAINC1',
                year_min=1969, 
                year_max=2023, 
                line_codes=['1','2','3']
            )

        if args.get_bea_gdp_data:
            get_bea_gdp_data(
                bea_api_key,
                table_name='CAGDP1',
                year_min=2017, # min year available is 2017 
                year_max=2023, 
                line_codes=['1','2','3']
            )

        if args.get_bls_regional_cpi:
            get_regional_bls_cpi_data(
                bls_api_key, 
                start_year=1969,
                end_year=2023
                )

        if args.get_bls_usa_cpi:
            get_usa_bls_cpi_data(
                bls_api_key, 
                start_year=1969,
                end_year=2023
                )
            
        if args.get_state_census_geodata:
            get_state_census_geo_file(
                "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_state_20m.zip"
            )

        if args.process_bea_data:
            process_bea_data(
                bea_income_file="data/interim/df_BEA_income_1969_2023.pickle",
                regional_cpi_file="data/interim/df_bls_regional_cpi_1969_2023.pickle", 
                usa_cpi_file = "data/interim/df_bls_usa_cpi_1969_2023.pickle",
                gdp_file = "data/interim/df_BEA_gdp_2017_2023.pickle"
                )
            
        if args.create_final_summary_dataset:
            create_final_summary_df(
                df_ranking_path="data/processed/CDC_PLACES_county_rankings.pickle", 
                df_bea_path="data/processed/bea_economic_data.pickle", 
                bea_year=2022,
                fileout_path="data/processed/df_summary_final.pickle"
                )
            
        if args.create_final_measures_dataset:
            create_final_measures_df(
                df_measures_path="data/processed/CDC_PLACES_county_measures.pickle",
                fileout_path="data/processed/df_measures_final.pickle"
                )
        if args.fit_gam:
            fit_gam(
                df_path = "data/processed/df_summary_final.pickle"
            )