# Section Titles
dashboard_information_title = "Dashboard Information"

# Developed by
developed_by = "JS Data Science Services LLC"

# Goal of Dashboard
dashboard_info_title = "Dashboard Overview"
#goal_of_dashboard = """
#The goal of this Dashboard is to provide comprehensive insights into the health status of U.S. counties by integrating data from various government sources, including CDC health metrics, BEA economic data, BLS CPI data, and Census geolocation data. 
#The UnHealth Score™ was created to provide an in-depth assessment of county-level health, aggregating data from a spectrum of health indicators, including chronic disease prevalence, lifestyle choices, and disability rates.
#The UnHealth Score™ facilitates direct comparisons between counties on all health metrics, clearly highlighting regions that necessitate urgent health interventions and support. 
#"""

# Tab Information
tab_information_title = "Views Information"

# Summary View Tab
summary_view_tab_title = "Summary View"
summary_view_tab_data = (
    "The Summary View tab provides a high-level overview of the health and economic status of U.S. counties, enabling users to explore and visualize key data points through interactive elements:"
    "\n\nInteractive Map:"
    "\nWhat it shows: The UnHealth scores of counties across the U.S., color-coded to indicate relative health status from healthier (green) to less healthy (red) based on the UnHealth Score."
    "\nFiltering options: Users can filter the map view by selecting specific states, allowing for a focused examination of regional health scores."
    "\nScatter Plot:"
    "\nWhat it shows: The relationship between per capita income and UnHealth Scores, illustrating how economic factors correlate with health outcomes. This chart is particularly useful for identifying patterns or outliers in how wealth and health interact across different counties."
    "\nTable of Rankings:"
    "\nWhat it shows: A list of counties with the best and worst health scores, alongside their income per capita and population. This table provides a snapshot of the extremes in health outcomes within the selected data set."
)

# GAM Model Description
gam_model_description = (
    "\nThe Generalized Additive Model (GAM) used in this tab is to aid in understanding the relationship between per capita income and health scores. Unlike traditional linear models, GAM can capture non-linear relationships without assuming a specific form of interaction between variables. This flexibility makes it suitable for revealing the underlying 'structure' of data relationships, especially when the connection between health scores and economic indicators is complex and not strictly linear."
    """\nThe GAM's value in this context lies more in exploratory data analysis and understanding data patterns rather than predictive accuracy. It helps us visualize how the UnHealth scores tend to vary with changes in per capita income across counties, providing a more accurate representation of this relationship than linear models. This approach was chosen after comparing with other models (linear, linear with log transformation), as GAM offered a better fit and visualization of the data's inherent relationships. 
        It is interesting to note where the GAM curve flattens out, indicating that at about $70,000, additional marginal income has a diminished affect on the UnHealth score."""
)

# County View Tab
county_view_tab_title = "County View"
county_view_tab_data = (
    "The County View tab displays into the specifics of a selected county's health score, economic data, and population details, presenting a detailed analysis through interactive charts and key performance indicators (KPIs)."
)

# Key Features of the County View Tab
county_view_key_features = (
    "Key Features of the County View Tab:"
    "\nCounty Selection: Users can choose a state and then a county to focus their analysis on, offering a granular look at local health and economic conditions."
    "\nHealth Score and Economic KPIs:"
    "\nDisplays the selected county's UnHealth score, ranking, and economic indicators like GDP per capita and income per capita, comparing these to national averages."
    "\nInteractive Map:"
    "\nShowcases the selected county"
    "\nHealth Metrics Chart:"
    "\nA comprehensive chart displays all the CDC PLACES health metrics for the selected county. Additionally, the contribution of each category of health metrics to the overall UnHealth score is shown."
    "\nEconomic Trends Charts:"
    "\nMultiple charts present the county's economic trends over time, including adjusted and current dollar income per capita and GDP per capita, alongside population growth."
    "\nUsers can toggle between adjusted dollars (accounting for inflation) and current dollars to view economic data."
)

# Measure View Tab
measure_view_tab_title = "Measure View"

measure_view_tab_data = (
    "The Measure View tab focuses on exploring health measures across U.S. counties, providing a detailed look at specific health metrics and their distribution by county throught the United States."
)

# Interactive Map
measure_view_interactive_map = (
    "Interactive Map\nWhat it shows: Displays the distribution of a selected health measure across all counties in a color-coded format, highlighting areas with higher or lower metric scores."
    "\nFiltering options: Users can filter by state to narrow down the geographical focus and by health measure to select which metric to display."
)

# Measure Selection Functionality
measure_selection_functionality = (
    "Measure Selection\nFunctionality: A dropdown menu allows users to select from various health measures, such as obesity rates or smoking prevalence, to visualize on the map and analyze in the table."
)

# State Filtering Functionality
state_filtering_functionality = (
    "State Filtering\nFunctionality: Another dropdown menu enables users to filter the map and subsequent analysis by one or multiple states, offering state-specific insights into the selected health measure."
)

# Color Coding
color_coding = (
    "Color Coding\nThe map's color-coding visually represents health measure scores across counties, using a green-to-red gradient. It's important to note that various measures have different scales; for example, one measure may range from 4% to 6%, while another may range from 10% to 40%. However, the color scale on the map always shows the range specific to the selected health measure. Green indicates better health outcomes (lower scores), and red shows areas of concern (higher scores), with colors assigned based on the data's distribution within that measure's range. Hovering over a county reveals detailed metrics, including its score and rank for the selected health measure, facilitating a quick and clear understanding of regional health patterns."
)

# Best and Worst Scores Table
best_worst_scores_table = (
    "Best and Worst Scores Table\nWhat it shows: Lists the ten counties with the best and worst scores for the selected health measure, providing a quick comparison of extremes within the chosen filter criteria."
    "\nDetails provided: For each listed county, the table shows the county name, state, the percentage value for the selected measure, and the county's rank in that measure."
)

# Section Titles
data_sources_title = "Data Sources"

# CDC Places for Health Measures
cdc_places_title = "CDC Places for Health Measures"
cdc_places_data = """
The CDC's PLACES (Population Level Analysis and Community Estimates) program provides detailed data on health metrics across the U.S. It provides granular insights at multiple geographic levels—county, city, census tract, and ZIP Code—on chronic diseases, health outcomes, and risk behaviors.
This is the main dataset for our dashboard, and we focus on the county level data.
"""

# BEA for economic and population data
bea_title = "BEA for economic and population data"
bea_data = """
The U.S. Bureau of Economic Analysis provides the data at the county level for personal income, GDP, and population.
"""

# Census for geo info
census_title = "Census for geo info"
census_data = """
We use data from the US Census Bureau for the geolocation data of the counties.
"""

# BLS for CPI data
bls_title = "BLS for CPI data"
bls_data = """
From the US Bureau of Labor Statistics, we obtain Consumer Price Index levels to adjust income-based levels.
Website: https://www.bls.gov/cpi/regional-resources.htm
"""

# Section Titles
data_loading_processing_title = "Data Loading and Processing Overview"

# CDC PLACES Data
cdc_places_loading_title = "CDC PLACES Data"
cdc_places_loading_data = """
Loading: CDC PLACES data for the years 2022 and 2023 is downloaded directly from the CDC website using provided URLs. Data for each year is loaded into a pandas DataFrame. Note that the year here does not indicate the date of the data collection, rather the date of the release.

Data Processing:
The datasets from 2022 and 2023 are concatenated.
Missing disability data for Florida counties is addressed by inserting the USA average for these locations.
Geographic information (Geolocation) for the data is parsed and converted to a GeoDataFrame, enabling spatial operations.
County-level geolocation data is downloaded from the U.S. Census Bureau and saved as a GeoJSON file.
The CDC data is spatially joined with the U.S. Census county data to enrich the dataset with additional geographic identifiers.
Data is filtered to include only age-adjusted prevalence measures.
Certain health measures are inverted to represent negative outcomes, enhancing data interpretation.
"""

# Processing and Creation of the UnHealth Score
unhealth_score_processing_title = "Processing and Creation of the UnHealth Score"
unhealth_score_processing_data = """
Data Cleanup and Normalization:
Initially, the data undergoes a cleanup phase to focus on county-specific information, removing any aggregate state data and ensuring that only the most recent entries for each health measure and county are retained. Subsequent normalization within health measure groups allows for comparison across different health metrics, acknowledging that each measure has its unique scale and distribution.

The UnHealth Score:
Normalization plays a crucial role in two key stages of the "UnHealth Score" calculation:
    Within-Group Normalization: Each health measure's values are normalized within their specific group to a scale of 0 to 100. This step is crucial for two reasons:
        Equitability: It ensures that all health measures contribute equally to the overall health assessment, despite the original scales and value ranges of the data. This prevents measures with naturally higher or more variable values from disproportionately affecting the overall health score.
        Comparability: Normalizing within groups makes it possible to compare health outcomes across different measures and counties on a common scale, facilitating an apples-to-apples comparison.
    Overall Score Normalization: After calculating the weighted scores for each county, these scores are normalized again to produce the "UnHealth Score" on a standardized 0 to 100 scale across all counties. This second layer of normalization serves to:
        Standardize Rankings: It provides a clear, intuitive metric for ranking counties, where a lower "UnHealth Score" directly indicates a healthier county. This standardized scale simplifies the interpretation and comparison of health statuses across the dashboard.
        Adjust for Impact Scores: Since health measures are weighted by their impact scores, this overall normalization accounts for the cumulative effect of these weights, ensuring that the final "UnHealth Score" reflects a balanced assessment of various health determinants.
"""

# Data Transformation and Output Generation
data_transformation_title = "Data Transformation and Output Generation"
data_transformation_data = """
In addition to calculating the "UnHealth Score", the process involves measure shortening and contribution analysis, culminating in the generation of detailed and summary datasets for dashboard integration.
This two-tier normalization process—first within health measure groups and then across all counties—ensures that the "UnHealth Score" is a fair, comparable, and interpretable metric that accurately reflects the health landscape across counties.
"""

# BEA GDP and Income Data
bea_gdp_income_title = "BEA GDP and Income Data"

# Loading and Processing for GDP
gdp_loading_title = "Loading and Processing for GDP"
gdp_loading_data = """
GDP data from the Bureau of Economic Analysis (BEA) for counties, states, and the country from 2017 to 2023 is loaded through API calls.
Data is requested for specified economic indicators (line codes) and concatenated into a single DataFrame.
The final GDP dataset is saved as a pickle file.
"""

# Loading and Processing for Income
income_loading_title = "Loading and Processing for Income"
income_loading_data = """
Similar to GDP, income data is loaded for a broader historical range (1969 to 2023).
The process involves making API calls for county, state, and national data, merging the results, and saving the compiled data as a pickle file.
"""

# BLS CPI Data
bls_cpi_title = "BLS CPI Data"

# Regional CPI Data
regional_cpi_title = "Regional CPI Data"
regional_cpi_data = """
Consumer Price Index (CPI) data for various U.S. regions from the Bureau of Labor Statistics (BLS) is loaded for a given date range.
The data is organized by region and saved as a pickle file.
"""

# USA CPI Data
usa_cpi_title = "USA CPI Data"
usa_cpi_data = """
National CPI data is similarly fetched and processed for the specified years.
The dataset focuses on annual averages and is saved as a pickle file.
"""


# BEA and BLS Data Further Processing
bea_bls_further_processing_title = "BEA and BLS Data Further Processing"

bea_bls_further_processing_text = """
We organize states into four major regions (West, Midwest, South, and Northeast) to adjust income by regional CPI (Consumer Price Index) values and \
    adjust per capita income data for inflation using the CPI, which enables us to present income values in a way that reflects true purchasing power over time. \
        This adjustment is crucial for comparing economic well-being across different years, as it accounts for the changing value of money.
We calculate GDP per capita for both real (inflation-adjusted) and current-dollar terms. This calculation involves dividing the total economic output, as measured by GDP, by the population size. The distinction between real and current-dollar GDP helps us distinguish between economic growth driven by actual increases in goods and services versus that driven by price changes.
After preparing and adjusting our economic indicators, we consolidate this information into a comprehensive dataset. This dataset includes adjusted income levels, GDP per capita figures, and population statistics, providing a detailed view of economic health across different regions and the nation over time.
To create the final summary dataset we merge the health rankings with GDP data and then with government spending data, ensuring each county's health, economic, and spending data align.
The final summary dataset includes year, geographic identifiers, location names, state details, health rankings, population, and GDP per capita.
"""

