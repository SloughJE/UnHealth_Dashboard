import os
import json

import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta


from openai import OpenAI

from .prompt import prompt_template


def load_files_for_summary(
        synthea_pickle_dir="data/Synthea/pickle_optimized_output/",
        df_unhealth_summary_path = "data/processed/df_summary_final.pickle", 
        df_unhealth_measures_path="data/processed/df_measures_final.pickle"
        ):

    print("loading data for all patients")
    allergies = pd.read_pickle(f"{synthea_pickle_dir}/allergies.pkl")
    careplans = pd.read_pickle(f"{synthea_pickle_dir}/careplans.pkl")
    conditions = pd.read_pickle(f"{synthea_pickle_dir}/conditions.pkl")
    encounters = pd.read_pickle(f"{synthea_pickle_dir}/encounters.pkl")
    immunizations = pd.read_pickle(f"{synthea_pickle_dir}/immunizations.pkl")
    medications = pd.read_pickle(f"{synthea_pickle_dir}/medications.pkl")
    procedures = pd.read_pickle(f"{synthea_pickle_dir}/procedures.pkl")
    observations = pd.read_pickle(f"{synthea_pickle_dir}/observations.pkl")
                                  
    # need patient data for county info:
    df_patient_info = pd.read_pickle(f"{synthea_pickle_dir}/patients.pkl")
    df_patient_info = df_patient_info[df_patient_info.DEATHDATE.isna()]
    df_patient_info = df_patient_info[df_patient_info.FIPS.notna()]
    df_patient_info['FIPS'] = df_patient_info['FIPS'].astype(int).astype(str).str.zfill(5)

    df_summary = pd.read_pickle(df_unhealth_summary_path)
    df_measures = pd.read_pickle(df_unhealth_measures_path)
    
    df_summary['Weighted_Score_Normalized'] = round(df_summary['Weighted_Score_Normalized'],2)

    df_measures['absolute_contribution'] = round(df_measures['absolute_contribution'],2)
    df_measures['Data_Value'] = round(df_measures['Data_Value'],2)
    df_measures['County Measure Rank'] = df_measures['County Measure Rank'].astype(int)
    
    # create QOLS data, lab data, and vital-signs dfs
    df_lab = observations[observations.CATEGORY=='laboratory'].copy()
    df_lab = df_lab[df_lab.TYPE=='numeric']
    #df_lab['VALUE'] = pd.to_numeric(df_lab.VALUE)

    df_vital_signs = observations[observations.CATEGORY=='vital-signs'].copy()
    #df_lab = df_lab[df_lab.TYPE=='numeric']
    #df_vital_signs['VALUE'] = pd.to_numeric(df_vital_signs.VALUE)

    df_qols_scores = observations[observations['DESCRIPTION'] == 'QOLS'].copy()
    #df_lab = df_lab[df_lab.TYPE=='numeric']
    #df_qols_scores['VALUE'] = pd.to_numeric(df_qols_scores.VALUE)
    
    
    return df_patient_info, allergies, careplans, conditions, encounters, immunizations, medications, procedures, df_lab, df_vital_signs, df_qols_scores, df_summary, df_measures


def get_data_for_single_patient(patient_id, *dataframes):
    # Unpack dataframes tuple into a dictionary
    dataframes_dict = dict(dataframes)
    columns_to_drop = [
        'PATIENT', 'PAYER', 'ENCOUNTER',
        'BASE_COST', 'PAYER_COVERAGE', 'DISPENSES', 'TOTALCOST',
        'Id',
        'ORGANIZATION', 'PROVIDER',
        'BASE_ENCOUNTER_COST', 'TOTAL_CLAIM_COST',
        'SSN','DRIVERS','PASSPORT',
    ]
    # Check if patient's FIPS value exists in df_summary
    filtered_df_info = dataframes_dict['df_patient_info'].loc[dataframes_dict['df_patient_info']['Id'] == patient_id].copy()
    fips_value = filtered_df_info['FIPS'].iloc[0] if not filtered_df_info.empty else None

    if fips_value not in dataframes_dict['df_summary']['GEOID'].values:
        print(f"Skipping patient {patient_id} because FIPS value not found in df_summary")
        return None

    dataframes_dict_new = {}

    for df_name, df in dataframes_dict.items():
        if df_name in ['df_patient_info', 'df_measures', 'df_summary']:
            # Use .copy(deep=True) to ensure you're working with a copy of the data
            filtered_df = df.loc[df['Id'] == patient_id].copy(deep=True) if df_name == 'df_patient_info' else df.loc[df['GEOID'] == fips_value].copy(deep=True) if fips_value is not None else pd.DataFrame()
        else:
            filtered_df = df.loc[df['PATIENT'] == patient_id].copy(deep=True) if 'PATIENT' in df.columns else df.loc[df['Id'] == patient_id].copy(deep=True)
            filtered_df.drop(columns=columns_to_drop, errors='ignore', inplace=True)
        df_name += '_patient'  # Modify the name to indicate it's specific to a patient
        dataframes_dict_new[df_name] = filtered_df

    return dataframes_dict_new



def extract_patient_summary(data):
    """
    Extracts and formats patient data into a narrative for AI processing.
    
    :param data: Dictionary of patient-related dataframes.
    :return: Formatted string prompt for AI model.
    """
    # Extract basic patient demographics
    patient_info = data['df_patient_info_patient'].iloc[0]
    age = 2024 - int(patient_info['BIRTHDATE'][:4])  # Example calculation for age
    patient_demographics = f"Patient Demographics:\n- Age: {age}\n- Gender: {patient_info['GENDER']}\n- Race: {patient_info['RACE']}, Ethnicity: {patient_info['ETHNICITY']}\n"

    # Format conditions
    # Check if the conditions DataFrame is not empty
    if not data['conditions_patient'].empty:
        five_years_ago = datetime.now() - timedelta(days=5*365)
        data['conditions_patient']['START'] = pd.to_datetime(data['conditions_patient']['START'])
        recent_conditions = data['conditions_patient'][data['conditions_patient']['START'] >= five_years_ago]
        
        if not recent_conditions.empty:
            conditions_list = "\n".join([
                f"- {row['DESCRIPTION']} (from {row['START'].strftime('%Y-%m-%d')} to {row.get('STOP', 'present')})"
                for index, row in recent_conditions.iterrows()])
            conditions_summary = f"Medical Conditions (Last 5 Years):\n{conditions_list}\n"
        else:
            conditions_summary = "No medical conditions recorded in the last 5 years.\n"
    else:
        conditions_summary = "No medical conditions data available.\n"
    
    
    # Identify current medications (where STOP is NaN)
    current_medications = data['medications_patient'][data['medications_patient']['STOP'].isna()]
    if not current_medications.empty:
        current_medications_list = "\n".join([
            f"- {row['DESCRIPTION']} (Started: {datetime.strptime(row['START'], '%Y-%m-%dT%H:%M:%SZ').strftime('%B %d, %Y')}, Reason: {'Not specified' if pd.isna(row['REASONDESCRIPTION']) else row['REASONDESCRIPTION']})"
            for index, row in current_medications.iterrows()
        ])
        current_medications_summary = f"Current Medications:\n{current_medications_list}\n"
    else:
        current_medications_summary = "Current Medications: None\n"

    # Historical Medications
    if not data['medications_patient'].empty:
        # Add a 'YEAR' column derived from the 'START' date for medications
        data['medications_patient']['YEAR'] = data['medications_patient']['START'].str[:4]

        # Group by 'DESCRIPTION' and count occurrences for historical medications
        historical_medications = data['medications_patient'][data['medications_patient']['STOP'].notna()]
        medications_grouped = historical_medications.groupby(['DESCRIPTION']).agg(
            year_min=pd.NamedAgg(column='YEAR', aggfunc='min'),
            year_max=pd.NamedAgg(column='YEAR', aggfunc='max'),
            count=pd.NamedAgg(column='YEAR', aggfunc='size')
        ).reset_index()

        historical_medications_summary = "Medication History by Type and Year Range:\n"
        for index, row in medications_grouped.iterrows():
            year_range = f"{row['year_min']}-{row['year_max']}" if row['year_min'] != row['year_max'] else f"{row['year_min']}"
            historical_medications_summary += f"- {row['DESCRIPTION']}: {row['count']} times ({year_range})\n"

    else:
        historical_medications_summary = "Historical Medications: None\n"

    medications_summary = f"{current_medications_summary}\n{historical_medications_summary}"


    # Process allergies
    if not data['allergies_patient'].empty:
        # Determine current vs. past allergies based on the presence of a STOP date
        current_allergies = data['allergies_patient'][data['allergies_patient']['STOP'].isna()]
        past_allergies = data['allergies_patient'][~data['allergies_patient']['STOP'].isna()]
        
        current_allergies_list = "\n".join([f"- {row['DESCRIPTION']}" for index, row in current_allergies.iterrows()])
        past_allergies_list = "\n".join([f"- {row['DESCRIPTION']}" for index, row in past_allergies.iterrows()])
        
        allergies_summary = f"Current Allergies:\n{current_allergies_list if not current_allergies.empty else 'None'}\n" \
                            f"Past Allergies:\n{past_allergies_list if not past_allergies.empty else 'None'}\n"
    else:
        allergies_summary = "Allergies Data: None\n"


    # Process care plans
    if not data['careplans_patient'].empty:
        # Add 'YEAR' column derived from the 'START' date for care plans
        data['careplans_patient']['YEAR'] = data['careplans_patient']['START'].str[:4]
        
        # Group by 'DESCRIPTION' and 'YEAR' and count occurrences for care plans
        careplans_grouped = data['careplans_patient'].groupby(['DESCRIPTION', 'YEAR']).size().reset_index(name='counts')
        careplans_grouped.sort_values(by=['DESCRIPTION', 'YEAR'], ascending=[True, True], inplace=True)
        
        careplans_summary = "Care Plan History by Type and Year:\n"
        current_description = ""
        for description, group in careplans_grouped.groupby('DESCRIPTION'):
            years = group['YEAR'].unique()
            year_range = f"{years.min()}-{years.max()}" if years.min() != years.max() else f"{years.min()}"
            count = group['counts'].sum()
            careplans_summary += f"- {description}: {count} times ({year_range})\n"
    else:
        careplans_summary = "Care Plan Data: None\n"

    # Format encounters
    # Group by 'DESCRIPTION' to aggregate data
    data['encounters_patient']['START'] = pd.to_datetime(data['encounters_patient']['START'])

    encounters_grouped = data['encounters_patient'].groupby('DESCRIPTION').agg(
        first_encounter=pd.NamedAgg(column='START', aggfunc='min'),
        last_encounter=pd.NamedAgg(column='START', aggfunc='max'),
        total_encounters=pd.NamedAgg(column='DESCRIPTION', aggfunc='count')
    ).reset_index()

    # Convert first and last encounter dates to just the year for simplicity
    encounters_grouped['first_encounter'] = encounters_grouped['first_encounter'].dt.year
    encounters_grouped['last_encounter'] = encounters_grouped['last_encounter'].dt.year

    # Sort for readability
    encounters_grouped.sort_values(by=['DESCRIPTION', 'first_encounter'], ascending=[True, True], inplace=True)

    # Generate summary
    encounters_summary = "Healthcare Encounters by Type and Year Range:\n"
    for index, row in encounters_grouped.iterrows():
        year_range = f"{row['first_encounter']}-{row['last_encounter']}" if row['first_encounter'] != row['last_encounter'] else f"{row['first_encounter']}"
        encounters_summary += f"- {row['DESCRIPTION']}: {row['total_encounters']} times ({year_range})\n"

    # Identify and add the latest encounter to the summary
    if not data['encounters_patient'].empty:
        latest_encounter = data['encounters_patient'].sort_values(by='START', ascending=False).iloc[0]
        latest_encounter_date = latest_encounter['START'].strftime('%B %d, %Y')
        encounters_summary += f"Latest Encounter: {latest_encounter['DESCRIPTION']} on {latest_encounter_date}\n"
    else:
        encounters_summary += "No encounters recorded.\n"

    # Format immunizations
    if not data['immunizations_patient'].empty:
        # Convert 'DATE' to datetime to work with it easily
        data['immunizations_patient']['DATE'] = pd.to_datetime(data['immunizations_patient']['DATE'])
        data['immunizations_patient']['YEAR'] = data['immunizations_patient']['DATE'].dt.year
        
        # Group by 'DESCRIPTION' to work with each type
        immunizations_summary = "Immunization History Summary by Type:\n"
        for description, group in data['immunizations_patient'].groupby('DESCRIPTION'):
            year_range = f"{group['YEAR'].min()}-{group['YEAR'].max()}" if group['YEAR'].min() != group['YEAR'].max() else f"{group['YEAR'].min()}"
            count = group['DESCRIPTION'].count()
            immunizations_summary += f"- {description}: {count} times ({year_range})\n"
    else:
        immunizations_summary = "No immunization records available.\n"

    # LABS get latest non-duplicated labs   
    if not data['df_lab_patient'].empty:
        # Convert 'DATE' to datetime to ensure sorting works on actual dates
        df_lab_patient = data['df_lab_patient']
        df_lab_patient['DATE'] = pd.to_datetime(df_lab_patient['DATE'])
        df_lab_patient['DESCRIPTION_LOWER'] = df_lab_patient['DESCRIPTION'].str.lower()
    
        # Function to assign a custom sort priority based on the description
        def custom_priority(description):
            if "in Serum or Plasma" in description:
                return 1
            elif "in Blood" in description:
                return 2
            else:
                return 3

        # Apply the custom priority to each row using the lowercase description
        df_lab_patient['PRIORITY'] = df_lab_patient['DESCRIPTION_LOWER'].apply(custom_priority)

        # Sort by the lowercase description, custom priority, and then by DATE to get the latest
        sorted_labs = df_lab_patient.sort_values(by=['DESCRIPTION_LOWER', 'PRIORITY', 'DATE'], ascending=[True, True, False])

        # Extract the base description without specifics to identify duplicates broadly
        sorted_labs['BASE_DESCRIPTION'] = sorted_labs['DESCRIPTION_LOWER'].str.extract(r'([^\[]+)')[0].str.strip()

        # Drop duplicates based on this broad lowercase description, keeping the most preferred and latest result
        latest_labs = sorted_labs.drop_duplicates(subset=['BASE_DESCRIPTION'], keep='first')

        # Format the results for the summary, using the original (case-sensitive) 'DESCRIPTION'
        lab_results_list = "\n".join([
            f"- {row['DESCRIPTION']}: {row['VALUE']} {row['UNITS']}"
            for _, row in latest_labs.iterrows()
        ])
        lab_results_summary = "Latest Lab Results:\n" + lab_results_list + "\n"
        
    else:
        lab_results_summary = "No lab results available.\n"
   
    # Format health measures
    health_measures_list = "\n".join([f"- {row['Measure_short']}: {row['Data_Value']} (Rank: {row['County Measure Rank']})" for index, row in data['df_measures_patient'].iterrows()])
    health_measures_summary = f"Local Health Measures:\n{health_measures_list}\n"

    # Overall health summary for the location
    summary_info = data['df_summary_patient'].iloc[0]
    health_summary = f"Local Health Summary:\n- Location: {summary_info['LocationName']}, {summary_info['StateDesc']}\n" \
                     f"- Population: {summary_info['Population']}\n" \
                     f"- Per Capita Income: ${summary_info['Per capita personal income']}\n" \
                     f"- UnHealth Score: {summary_info['Weighted_Score_Normalized']} (Rank: {summary_info['Rank']})\n"

    public_health_context = health_measures_summary + health_summary

    # Combine all summaries
    prompt = (f"{patient_demographics}\n{conditions_summary}\n{medications_summary}\n"
              f"{allergies_summary}\n{immunizations_summary}\n{lab_results_summary}\n"
              f"{encounters_summary}\n{careplans_summary}\n{public_health_context}")
    
    return prompt


def save_summary_to_json(patient_id, summary_text, summaries_dir="data/processed/AI_summaries"):
    # Ensure the directory exists
    if not os.path.exists(summaries_dir):
        os.makedirs(summaries_dir)
    
    # Construct the file path using an f-string for string formatting
    file_path = f"{summaries_dir}/{patient_id}.json"
    
    # Data to be saved
    data = {
        "patient_id": patient_id,
        "summary": summary_text
    }
    
    # Write the JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    

def send_patient_summary_to_openai_and_save(prompt_template, patient_summary, patient_id,open_ai_key):

    client = OpenAI(api_key=open_ai_key)

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": patient_summary}
        ],
        temperature=0.01,
    )
    # Check if a summary was generated
    if chat_completion.choices and chat_completion.choices[0].message.content.strip():
        summary_text = chat_completion.choices[0].message.content

        # Save the summary along with the patient ID
        save_summary_to_json(patient_id, summary_text)
    else:
        # Print out the patient ID for which no summary was generated
        print(f"No summary generated for Patient ID: {patient_id}")
        # Even if no summary, you might still want to save a placeholder or log this event
        save_summary_to_json(patient_id, "No summary generated")


def create_AI_patient_summary(open_ai_key):

    df_patient_info, allergies, careplans, conditions, encounters, immunizations, medications, procedures, df_lab, df_vital_signs, df_qols_scores, df_summary, df_measures = load_files_for_summary()    

    # get list of all patients
    all_patients = list(df_patient_info.Id.unique())

    all_patients = all_patients[0:50]

    print(f"Creating summaries for {len(all_patients)} patients")

    for patient_id in tqdm(all_patients, desc="Processing Patients"):
        #'0156338a-987d-498b-5e6a-ab8f8e46cfad'
        patient_data = get_data_for_single_patient(patient_id, 
                                                    ('df_patient_info', df_patient_info),
                                                    ('allergies', allergies), 
                                                    ('careplans', careplans), 
                                                    ('conditions', conditions), 
                                                    ('encounters', encounters), 
                                                    ('immunizations', immunizations), 
                                                    ('medications', medications), 
                                                    ('procedures', procedures), 
                                                    ('df_lab', df_lab), 
                                                    ('df_vital_signs', df_vital_signs), 
                                                    ('df_qols_scores', df_qols_scores), 
                                                    ('df_summary', df_summary), 
                                                    ('df_measures', df_measures))
        

        if patient_data is None:
            print(f"Data for patient ID {patient_id} could not be processed. Skipping to next patient.")
            continue 

        patient_summary = extract_patient_summary(patient_data)
        #print(patient_summary)
        send_patient_summary_to_openai_and_save(prompt_template, patient_summary, patient_id,open_ai_key)


def save_patient_labs(
        synthea_pickle_dir="data/Synthea/pickle_optimized_output/",
        output_dir="data/processed/patient_labs"
        ):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("loading and processing patient observation data")
    observations = pd.read_pickle(f"{synthea_pickle_dir}/observations.pkl")
    
    # create QOLS data, lab data, and vital-signs dfs
    df_lab = observations[observations.CATEGORY=='laboratory'].copy()
    df_lab = df_lab[df_lab.TYPE=='numeric']
    df_lab['VALUE'] = pd.to_numeric(df_lab.VALUE)
    df_lab['DATE'] = pd.to_datetime(df_lab['DATE'])

    df_vital_signs = observations[observations.CATEGORY=='vital-signs'].copy()
    df_vital_signs = df_vital_signs[df_vital_signs.TYPE=='numeric']
    df_vital_signs['VALUE'] = pd.to_numeric(df_vital_signs.VALUE)
    df_vital_signs['DATE'] = pd.to_datetime(df_vital_signs['DATE'])

    df_qols_scores = observations[observations['DESCRIPTION'] == 'QOLS'].copy()
    df_qols_scores = df_qols_scores[df_qols_scores.TYPE=='numeric']
    df_qols_scores['VALUE'] = pd.to_numeric(df_qols_scores.VALUE)
    df_qols_scores['DATE'] = pd.to_datetime(df_qols_scores['DATE'])

    columns_to_drop = [
      'ENCOUNTER',
      'CATEGORY',
      'CODE',
      'TYPE'
    ]
    df_lab.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    df_vital_signs.drop(columns=columns_to_drop, errors='ignore', inplace=True)
    df_qols_scores.drop(columns=columns_to_drop, errors='ignore', inplace=True)


    def keep_latest_labs(df_group):
        return df_group.head(1000)

    df_lab = df_lab.sort_values(by=['PATIENT', 'DATE'], ascending=[True, False])
    df_lab = df_lab.groupby('PATIENT').apply(keep_latest_labs).reset_index(drop=True)

    df_vital_signs = df_vital_signs.sort_values(by=['PATIENT', 'DATE'], ascending=[True, False])
    df_vital_signs = df_vital_signs.groupby('PATIENT').apply(keep_latest_labs).reset_index(drop=True)

    df_qols_scores = df_qols_scores.sort_values(by=['PATIENT', 'DATE'], ascending=[True, False])
    df_qols_scores = df_qols_scores.groupby('PATIENT').apply(keep_latest_labs).reset_index(drop=True)

    #patient_row_counts = df_vital_signs.groupby('PATIENT').size()
    #patient_row_counts_sorted_by_count_desc = patient_row_counts.sort_values(ascending=False)
    #print(patient_row_counts_sorted_by_count_desc.head(20))
    #patient_row_counts_sorted_by_count_desc = patient_row_counts.sort_values(ascending=True)
    #print(patient_row_counts_sorted_by_count_desc.head(20))

    #print(df_lab[df_lab.PATIENT=='1310eed2-dd47-7cd3-01d9-7a362182e402'].head())
    print("number of unique labs BEFORE filtering:")
    print(len(df_lab.DESCRIPTION.unique()))
    #print(df_lab.DESCRIPTION.unique())

    # Define the list of important labs with their units
    # we have too many labs to show so we take just the 'important' ones (obv this is subjective)
    # Simplified list of important labs without specifying medium, all lowercase
    important_labs_normalized = [
        "hemoglobin a1c/hemoglobin.total",
        "glucose",
        "creatinine",
        "urea nitrogen",
        "cholesterol",
        "triglycerides",
        "low density lipoprotein cholesterol",
        "hemoglobin",
        "hematocrit",
        "leukocytes",
        "glomerular filtration rate/1.73 sq m.predicted",
        "potassium",
        "sodium",
        "alanine aminotransferase",
        "aspartate aminotransferase",
    ]

    def normalize_lab_description(description):
        # Remove specifics about the medium and convert to lowercase for uniformity
        normalized = description.split('[')[0].strip().lower()
        return normalized
    # Normalize lab descriptions for generalization
    df_lab['NORMALIZED_DESCRIPTION'] = df_lab['DESCRIPTION'].apply(normalize_lab_description)
    df_lab = df_lab[df_lab['NORMALIZED_DESCRIPTION'].isin(important_labs_normalized)]

    # Determine priority for "in Serum or Plasma" > "in Blood" > others
    def determine_priority(description):
        if "in serum or plasma" in description.lower():
            return 1
        elif "in blood" in description.lower():
            return 2
        else:
            return 3

    df_lab['PRIORITY'] = df_lab['DESCRIPTION'].apply(determine_priority)
    
    df_lab = df_lab.sort_values(by=['PATIENT', 'NORMALIZED_DESCRIPTION', 'PRIORITY', 'DATE'], ascending=[True, True, True, False])

    # Group by 'PATIENT' and 'NORMALIZED_DESCRIPTION' to handle each lab type for each patient separately
    grouped = df_lab.groupby(['PATIENT', 'NORMALIZED_DESCRIPTION'])

    # Initialize an empty DataFrame to hold the filtered lab records
    filtered_labs = pd.DataFrame()

    for _, group in grouped:
        # Within each group, further group by 'DESCRIPTION' to separate different mediums (e.g., 'in Serum' vs. 'in Blood')
        subgroups = group.groupby('DESCRIPTION')
        
        # Initialize a variable to track the best priority seen so far (lower is better)
        best_priority = group['PRIORITY'].min()
        
        for description, subgroup in subgroups:
            # Check if the current subgroup's priority matches the best priority for this lab type
            if subgroup['PRIORITY'].iloc[0] == best_priority:
                # If so, append this subgroup to the filtered_labs DataFrame
                filtered_labs = pd.concat([filtered_labs, subgroup])
                break  # Stop looking at other subgroups for this lab type since we found the highest priority one

    df_lab = filtered_labs.sort_values(by=['PATIENT', 'DATE'], ascending=[True, True])

    df_lab.drop(columns=["NORMALIZED_DESCRIPTION","PRIORITY"], errors='ignore', inplace=True)

    print("number of unique labs AFTER filtering:")
    #print(len(df_lab[df_lab.PATIENT=='1310eed2-dd47-7cd3-01d9-7a362182e402'].DESCRIPTION.unique()))
    print(f"num unique labs ALL: {len(df_lab.DESCRIPTION.unique())}")
    print(df_lab.DESCRIPTION.unique())

    #print(df_vital_signs[df_vital_signs.PATIENT=='1ad0f32b-5c6c-e747-5fa8-65c6cb790359'].head())
    print("number of unique vital signs:")
    print(len(df_vital_signs[df_vital_signs.PATIENT=='1ad0f32b-5c6c-e747-5fa8-65c6cb790359'].DESCRIPTION.unique()))


    # final dfs:
    print("labs:")
    print(df_lab.head(2))
    print("vital signs:")
    print(df_vital_signs.head(2))
    print("QOLS:")
    print(df_qols_scores.head(2))

    df_lab.to_pickle(f"{output_dir}/df_patient_labs.pkl")
    df_vital_signs.to_pickle(f"{output_dir}/df_vital_signs.pkl")
    df_qols_scores.to_pickle(f"{output_dir}/df_qols_scores.pkl")

    print(f"patient data saved to {output_dir}")
