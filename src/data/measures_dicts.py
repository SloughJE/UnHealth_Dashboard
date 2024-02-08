

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

impact_scores = {
    "Stroke among adults aged >=18 years": 5,
    "Chronic obstructive pulmonary disease among adults aged >=18 years": 5,
    "Cancer (excluding skin cancer) among adults aged >=18 years": 5,
    "Diagnosed diabetes among adults aged >=18 years": 5,
    "Coronary heart disease among adults aged >=18 years": 5,
    "Chronic kidney disease among adults aged >=18 years": 5,
    "Cognitive disability among adults ages >=18 years": 5,
    "Self-care disability among adults aged >=18 years": 5,

    "Current smoking among adults aged >=18 years": 4,
    "Obesity among adults aged >=18 years": 4,
    "Depression among adults aged >=18 years": 4,
    "Binge drinking among adults aged >=18 years": 4,
    "Mental health not good for >=14 days among adults aged >=18 years": 4,
    "Mobility disability among adults aged >=18 years": 4,
    "High blood pressure among adults aged >=18 years": 4,
    "Independent living disability among adults aged >=18 years": 4,
    "Vision disability among adults aged >=18 years": 4,
    "Any disability among adults aged >=18 years": 4,

    "Arthritis among adults aged >=18 years": 3,
    "No leisure-time physical activity among adults aged >=18 years": 3,
    "Physical health not good for >=14 days among adults aged >=18 years": 3,
    "Fair or poor self-rated health status among adults aged >=18 years": 3,
    "All teeth lost among adults aged >=65 years": 3,
    "Current lack of health insurance among adults aged 18-64 years": 3,

    "High cholesterol among adults aged >=18 years who have been screened in the past 5 years": 2,
    "Sleeping less than 7 hours among adults aged >=18 years": 2,
    "Current asthma among adults aged >=18 years": 2,
    "Not taking medicine for high blood pressure among adults aged >=18 years": 2,
    "Older adult men aged >=65 years not up to date on clinical preventive services": 2,
    "Older adult women aged >=65 years not up to date on clinical preventive services": 2,

    "No mammography use among women aged 50-74 years": 1,
    "No colorectal cancer screening among adults aged 50-75 years": 1,
    "No cervical cancer screening among adult women aged 21-65 years": 1,
    "No doctor visit for checkup in past year among adults aged >=18 years": 1,
    "No dental visit in past year among adults aged >=18 years": 1,
    "No cholesterol screening among adults aged >=18 years": 1,
    "Hearing disability among adults aged >=18 years": 1
}

# dict for shortening the Measures
measure_replacements = {
    'All teeth lost among adults aged >=65 years': 'All teeth lost (>=65)',
    'Arthritis among adults aged >=18 years': 'Arthritis (>=18)',
    'Binge drinking among adults aged >=18 years': 'Binge drinking (>=18)',
    'Cancer (excluding skin cancer) among adults aged >=18 years': 'Cancer (>=18)',
    'Chronic kidney disease among adults aged >=18 years': 'Chronic kidney disease (>=18)',
    'Chronic obstructive pulmonary disease among adults aged >=18 years': 'COPD (>=18)',
    'Coronary heart disease among adults aged >=18 years': 'Coronary heart disease (>=18)',
    'Current asthma among adults aged >=18 years': 'Current asthma (>=18)',
    'Current lack of health insurance among adults aged 18-64 years': 'Lack of insurance (18-64)',
    'Current smoking among adults aged >=18 years': 'Current smoking (>=18)',
    'Depression among adults aged >=18 years': 'Depression (>=18)',
    'Diagnosed diabetes among adults aged >=18 years': 'Diagnosed diabetes (>=18)',
    'Fair or poor self-rated health status among adults aged >=18 years': 'Poor health self-rating (>=18)',
    'Mental health not good for >=14 days among adults aged >=18 years': 'Poor mental health (>=18)',
    'No cervical cancer screening among adult women aged 21-65 years': 'No cervical cancer screening (21-65)',
    'No colorectal cancer screening among adults aged 50-75 years': 'No colorectal cancer screening (50-75)',
    'No dental visit in past year among adults aged >=18 years': 'No dental visit (>=18)',
    'No doctor visit for checkup in past year among adults aged >=18 years': 'No doctor visit (>=18)',
    'No leisure-time physical activity among adults aged >=18 years': 'No physical activity (>=18)',
    'No mammography use among women aged 50-74 years': 'No mammography use (50-74)',
    'Obesity among adults aged >=18 years': 'Obesity (>=18)',
    'Older adult men aged >=65 years not up to date on clinical preventive services': 'Men not up to date: clinical preventive (>=65)',
    'Older adult women aged >=65 years not up to date on clinical preventive services': 'Women not up to date: clinical preventive (>=65)',
    'Physical health not good for >=14 days among adults aged >=18 years': 'Poor physical health (>=18)',
    'Sleeping less than 7 hours among adults aged >=18 years': 'Sleeping < 7 hours (>=18)',
    'Stroke among adults aged >=18 years': 'Stroke (>=18)',
    'Any disability among adults aged >=18 years':'Any disability (>=18)',
    'Cognitive disability among adults ages >=18 years':'Cognitive disability (>=18)',
    'Hearing disability among adults aged >=18 years': 'Hearing disability (>=18)',
    'Independent living disability among adults aged >=18 years':'Independent living disability (>=18)',
    'Mobility disability among adults aged >=18 years': 'Mobility disability (>=18)',
    'Self-care disability among adults aged >=18 years': 'Self-care disability (>=18)',
    'Vision disability among adults aged >=18 years': 'Vision disability (>=18)',
    'High blood pressure among adults aged >=18 years': 'High blood pressure (>=18)',
    'High cholesterol among adults aged >=18 years who have been screened in the past 5 years': 'High cholesterol if screening last 5 yrs (>=18)',
    'No cholesterol screening among adults aged >=18 years': 'No cholesterol screening (>=18)',
    'Not taking medicine for high blood pressure among adults aged >=18 years': 'Not on hypertension medicine (>=18)'
}
