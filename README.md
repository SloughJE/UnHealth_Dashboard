# [The UnHealth Dashboard](https://unhealth-dashboard-6d75504325c4.herokuapp.com/)

**Developed by**: [JS Data Science Services LLC](https://sloughje.github.io/)

## Dashboard Overview

The Dashboard aims to deliver insights into U.S. county health by combining CDC health metrics, BEA economic data, BLS CPI data, and Census geolocation data. At its core is the UnHealth Score™, designed to assess county health comprehensively. This score aggregates various health indicators, facilitating direct county comparisons and highlighting areas needing health interventions.

### Views Information

#### Summary View

- **Interactive Map**: Shows UnHealth scores across counties, color-coded from healthier (green) to less healthy (red).
- **Scatter Plot**: Illustrates the relationship between per capita income and UnHealth Scores, identifying economic-health patterns.
- **Table of Rankings**: Lists counties with the best and worst health scores, income per capita, and population.

#### County View

Focuses on a selected county’s details, offering in-depth analysis through interactive charts and key performance indicators (KPIs). Features include county selection, health score and economic KPIs display, an interactive map, health metrics chart, and economic trends charts.

#### Measure View

Explores specific health measures across counties, featuring an interactive map for visualizing the distribution of health metrics, measure selection functionality, and a table listing the best and worst scores for the selected health measure.


# Dashboard Data Processing Workflow

## Overview

This outlines the steps taken to process data for our dashboard, which uses health metrics from CDC PLACES and economic indicators from the Bureau of Economic Analysis (BEA) and inflation data from the Bureau of Labor Statistics (BLS).

## Processing Steps

### CDC PLACES Health Data

1. **Getting Data**: We download CDC PLACES data for 2022 and 2023 directly from the CDC API for the latest health metrics.
2. **Merging Data**: We combine data from different years into one dataset for analysis.
3. **Filling Gaps**: For missing disability data in Florida, we use U.S. averages to keep our dataset complete.
4. **Using Maps**: We add geographical data from U.S. census to help visualize health metrics on maps.
5. **Adjusting Metrics**: We flip certain health measures to keep consistency across all data. We also prioritize health metrics based on their impact on community health.
6. **Ranking**: We rank counties based on health metrics after normalizing their values for fair comparison.
7. **Summary**: We calculate and summarize the health status of counties, focusing on key health metrics.

### Economic Data from BEA and Inflation Data from BLS

1. **Economic Data Fetching**: We pull income and GDP data for counties, states, and the nation from BEA, and inflation trends from BLS.
2. **Organizing Data**: We organize this data into usable formats, making sure we capture all necessary details.
3. **Combining and Cleaning**: We merge different datasets, clean them up, and prepare them for analysis, ensuring geographic identifiers match up where needed.
4. **Inflation Adjustment**: We adjust economic figures for inflation using CPI data, making sure we're comparing real values over time.

### Final Dataset Creation

1. **Matching FIPS Codes**: We check and match FIPS codes across health and economic datasets, correcting any discrepancies.
2. **Creating Datasets**: We make two summary datasets:
   - One combines health rankings with economic data for a complete view of each county.
   - The other details health measures by county, providing insights into specific health outcomes and behaviors.
3. **Adjustments and Notes**: We adjust data for inflation and add notes to clarify any changes or data sources used.

### Output

The final datasets are structured and saved for use in our dashboard, providing a comprehensive view of health and economic conditions across the U.S. This workflow ensures our dashboard offers up-to-date and accurate information for analysis.


# Project Default Flow Diagram

```mermaid
    graph TD
    A[Start] --> B{Data Acquisition}
    B --> C[Get CDC PLACES Data]
    B --> D[Get BEA Income Data]
    B --> E[Get BEA GDP Data]
    B --> F[Get Regional BLS CPI Data]
    B --> G[Get USA BLS CPI Data]
    C --> H[Initial Processing CDC PLACES Data]
    H --> I[Process CDC Data]
    D --> J[Process BEA Data]
    E --> J
    F --> J
    G --> J
    I --> K[Create Final Summary Dataset]
    I --> L[Create Final Measures Dataset]
    J --> K
    J --> L
    K --> M[Fit GAM Model]
    K --> N{Dashboard Setup}
    L --> N
    M --> N
    N --> O[Summary View Tab]
    N --> P[County View Tab]
    N --> Q[Measure View Tab]
    N --> R[Info View Tab]
    O --> S[Display Summary View]
    P --> T[Display County Specific Data]
    Q --> U[Display Health Measures Across Counties]
    R --> V[Display Dashboard Information]
    S --> W[main_app Dashboard]
    T --> W
    U --> W
    V --> W

```
