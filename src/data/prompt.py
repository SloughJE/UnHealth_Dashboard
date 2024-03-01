prompt_template = """
Objective: To provide a comprehensive and concise summary of a patient's medical history, current health status, and relevant public health data from their county, facilitating informed and personalized care during a consultation with a GP Medical Doctor.

Please format the summary as follows:
- Ensure that each section starts with a clear heading formatted as a heading (H2), followed by a colon (e.g., ##Patient Demographics and Background:).
- Use **bold** for key terms and important health conditions.
- Use *italic* for any advice or recommendations.
- Under each heading, list relevant points as bullet points.
- For the Local Public Health Context, start with a brief introduction to the county's health status, followed by bullet points for relevant specific measures, especially given the patient's history. The Local Health Measures state the prevelance of a health status (Data_Value), with their absolute_contribution to the UnHealth Score, and the rank per county. The (>=18) indicates the age. The Local Health Summary states the UnHealth Score and rank. 
- Conclude the summary with a clear call to action or next steps under the "Preparation for Consultation" heading.


The content of the patient summary:

Patient Summary:
- Provide a one or two line overall summary of current patient health.
- Note the most important and pressing items for this patient that may be relevant for this consulation.

Patient Demographics and Background:
- Extract and display basic demographic information, including age, sex, and primary language.

Medical History Overview:
- Summarize chronic conditions, past medical history, and family history, highlighting significant events and their implications on the patient's health.

Current Medications and Allergies:
- List current medications, including any recent changes, and highlight known allergies, emphasizing their relevance to treatment and care planning.

Recent Healthcare Encounters:
- Provide details of the most recent visits, including diagnostics, treatment adjustments, and any specialist consultations.

Vaccination Status:
- Review and summarize the vaccination history, noting any gaps in immunization and potential risks.

Lifestyle Factors:
- Discuss lifestyle factors that may impact health, including diet, exercise, substance use, and mental health, inferred from medical records and patient interactions.

Lab Results and Numeric Health Data:
- Highlight the most recent lab results and any concerning trends, focusing on implications for the patient's health and treatment plan.

Quality of Life:
- Discuss the patient's quality of life and any changes over time, as indicated by quality of life scores and patient-reported outcomes.

Local Public Health Context:
- Utilize local health measures to discuss common health problems in the patient's county, including health outcomes, behavioral risk factors, and preventive measures. Reference the county's health ranking and the UnHealth Score™, emphasizing how this broader context might affect the patient's health.
- Integrate and analyze the measures with actual patient data.
- Note the UnHealth Score and indicate the relitive severity (low, medium, high) of health problems in the patient's county. (the UnHealth Score: Combines multiple health indicators from CDC PLACES data into 1 metric, Range from 0 to 100, higher is more UnHealthy, Includes chronic diseases, lifestyle factors, prevention, and disabilities, Each indicator is weighted; indicators like stroke, diabetes, and cancer have high impact; others like sleep duration, lower impact, Economic data is not factored into the UnHealth score)

Preparation for Consultation:
- Review the patient's concerns and any questions they may have, preparing to address these during the consultation. Consider preventive healthcare measures or screenings based on the patient's profile and local health data.

"""

