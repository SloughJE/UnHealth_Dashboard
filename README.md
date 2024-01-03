# Running the Pipelines

1) Explore the Jupyter notebook in `notebooks/ML_starter.ipynb`
2) Create a 'raw' data file by using this notebook. Note the commented out line `# df.to_csv('../data/raw/test.csv',index=False)`. Uncomment this to write out the CSV in the `data/raw` folder.
3) In `run_pipelines.py`, when you execute `python run_pipelines.py --load_data`, the `load_raw_data` function from `src/data/load_data.py` is run. It takes an input and output directory as arguments. These are currently set in `run_pipelines.py`. You can modify this function as you like, this is just a very basic example.
4) Add more steps to the pipeline such as: make_features, train_model, predict/score model...etc

An example of how to run a step in the pipeline: 
- load raw data
    - in integrated terminal run:
    - ```python run_pipelines.py --load_data```
Example of next logical step:
- create features for ML model
    - ```python run_pipelines.py --make_features```
Of course you have to write that function and the command to run it in `run_pipelines.py`

Create new pipelines following this method, adding to run_pipelines.py

# Codespace 
You can also open this project in codespace. On github, look at the green button above, ```use this template```, click on it and ```open in a codespace```. It will open this project in a web-based VSCode environment and build the container. You can run the notebook or pipelines here.


# Directory Structure

```
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── raw            <- The original, immutable data dump.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── results        <- results
│
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`. Usually the notebooks would be used to explore the data and possible different models.
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment
│
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── data           <- Scripts to download or generate data
│   │   └── load_dataset.py
│   │
│   ├── features       <- Scripts to turn raw data into features for modeling
│   │   └── make_features.py
│   │
│   ├── models         <- Scripts to train models and then use trained models to make
│   │   │                 predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   │
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
│
└──params.yml          <- parameters 
```

This template is inspired by the [cookiecutter data science template](https://github.com/drivendata/cookiecutter-data-science). Their template has a lot of stuff we don't use. 