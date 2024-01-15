import sys 
import yaml
import argparse

from src.data.load_data import load_process_CDC_PLACES_data
#from src.features.make_features import *
#from src.models import predict_model
#from src.models import train_model
# etc

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--get_CDC_LOCALS_data",
        help="load raw data",
        action="store_true"
    )
     
    parser.add_argument(
        "--make_features",
        help="make features",
        action="store_true"
    )
    # etc

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print("No arguments, please add arguments")
    else:
        with open("params.yaml") as f:
            params = yaml.safe_load(f)

        if args.get_CDC_LOCALS_data:
            load_process_CDC_PLACES_data(save_og_files=True)

