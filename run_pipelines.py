import sys 
import yaml
import argparse

from src.data.load_data import load_process_CDC_PLACES_data, rank_counties_by_year
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
        "--make_features",
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

