import sys 
import yaml
import argparse

from src.data.load_data import load_process_CDC_PLACES_data, rank_counties_by_year, process_gdp_data, get_spending_data
from src.data.merge_data import merge_gdp_ranking_data

#from src.features.make_features import *
#from src.models import predict_model
#from src.models import train_model
# etc

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--get_CDC_LOCALS_data",
        help="load and process raw data from CDC",
        action="store_true"
    )
    parser.add_argument(
        "--rank_counties_by_year",
        help="create a subjective ranking of counties by year",
        action="store_true"
    )

    parser.add_argument(
        "--process_gdp",
        help="make features",
        action="store_true"
    )

    parser.add_argument(
        "--get_spending",
        help="make features",
        action="store_true"
    )

    parser.add_argument(
        "--merge_ranking_gdp_spending",
        help="make features",
        action="store_true"
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print("No arguments, please add arguments")
    else:
        with open("params.yaml") as f:
            params = yaml.safe_load(f)

        if args.get_CDC_LOCALS_data:
            load_process_CDC_PLACES_data(save_og_files=True)

        if args.rank_counties_by_year:
            rank_counties_by_year(CDC_filepath="data/interim/CDC_PLACES_GEOID.pickle")

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


