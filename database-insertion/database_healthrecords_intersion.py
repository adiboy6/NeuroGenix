import sqlite3
from faker import Faker

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Initialize Faker
fake = Faker()

# Extract PatientIDs from the Patient table
c.execute('SELECT PatientID FROM Patient')
patient_ids = c.fetchall()

vitals = ["Blood pressure within normal range, heart rate steady at 72 beats per minute, and oxygen saturation at 98%.",
          "Healthy vitals recorded: Blood pressure 120/80 mmHg, heart rate 65 bpm, and respiratory rate 16 breaths per minute.",
          "Vital signs stable with a blood pressure of 110/70 mmHg, heart rate of 80 bpm, and oxygen saturation of 97%.",
          "Normal health indicators: Blood pressure 118/76 mmHg, heart rate 70 bpm, and respiratory rate 14 breaths per minute.",
          "Steady vitals observed: Blood pressure 122/78 mmHg, heart rate 68 bpm, and oxygen saturation at 99%.",
          "Patient presents with optimal health vitals: Blood pressure 115/75 mmHg, heart rate 62 bpm, and respiratory rate 18 breaths per minute.",
          "Vitals within healthy parameters: Blood pressure 126/82 mmHg, heart rate 75 bpm, and oxygen saturation 96%.",
          "Well-maintained health vitals recorded: Blood pressure 112/72 mmHg, heart rate 78 bpm, and respiratory rate 20 breaths per minute.",
          "Stable health indicators with blood pressure of 124/80 mmHg, heart rate 70 bpm, and oxygen saturation 98%.",
          "Normal vital signs observed: Blood pressure 118/76 mmHg, heart rate 72 bpm, and respiratory rate 16 breaths per minute."]

medication = ["Patient prescribed a daily regimen of 10 mg of atorvastatin for cholesterol management.",
              "Medication plan includes a twice-daily dose of 500 mg amoxicillin for a week to treat bacterial infection.",
              "Prescribed a low-dose aspirin (81 mg) as a preventive measure for cardiovascular health.",
              "Patient advised to take a 50 mg tablet of sertraline daily for management of generalized anxiety disorder.",
              "Prescription for a 20 mg dose of omeprazole to be taken before meals for acid reflux relief.",
              "Antihypertensive regimen initiated with a daily dose of 5 mg amlodipine for blood pressure control.",
              "Patient instructed to use a 200 mcg fluticasone inhaler twice daily for asthma maintenance.",
              "Prescribed a 500 mg acetaminophen tablet for pain relief as needed.",
              "Oral contraceptive regimen established with a daily intake of 30 mcg ethinyl estradiol and 150 mcg levonorgestrel.",
              "Antibiotic course initiated with a seven-day supply of 250 mg ciprofloxacin for urinary tract infection treatment."]

diagnosis = ["MRI reveals normal brain anatomy with no detectable abnormalities.",
           "Structural MRI indicates no evidence of focal lesions or abnormalities in the cerebral cortex.",
           "MRI scan demonstrates intact white matter integrity and no signs of atrophy.",
           "Functional MRI highlights active regions in the frontal and parietal lobes during a cognitive task.",
           "Neuroimaging shows a well-defined tumor in the left temporal lobe with no signs of metastasis.",
           "MRI findings reveal increased signal intensity in the hippocampus, suggestive of early-stage neurodegeneration.",
           "Structural MRI demonstrates a small lesion in the cerebellum, likely indicative of a benign cyst.",
           "Functional connectivity MRI displays altered connectivity patterns in the default mode network in patients with schizophrenia.",
           "Diffusion tensor imaging reveals disrupted white matter tracts in the corpus callosum, consistent with traumatic brain injury.",
           "MRI scan confirms the presence of multiple sclerosis plaques in the white matter, indicative of disease activity.",
           "MRI scan displays brain degeneration, indicating possibility of Alzheimer's disease"]

allergies = ["No Known Allergies",
             "Patient reports a known allergy to penicillin, prompting avoidance of related antibiotics.",
             "Documented allergic reaction to shellfish; strict avoidance advised in dietary choices.",
             "History of hay fever confirmed, with allergies to grass and tree pollen identified.",
             "Patient exhibits sensitivity to bee stings, requiring an emergency anaphylaxis action plan.",
             "Allergic to latex; medical personnel alerted to use latex-free materials during procedures.",
             "Confirmed allergy to peanuts; strict avoidance and carrying an epinephrine auto-injector recommended.",
             "Patient reports adverse reactions to sulfa drugs; alternative medications explored.",
             "Allergy to dust mites identified; advised on environmental control measures for home.",
             "Seasonal allergy to ragweed documented; antihistamines prescribed for symptom relief.",
             "Known allergic reaction to cats; avoidance and use of antihistamines recommended for exposure."]

# Insert data into HealthRecords table
for i, (patient_id,) in enumerate(patient_ids):
    health_records_data = (
        f'ImagingID{i}',  # RecordID
        fake.random_element(elements=medication),  # Medications
        fake.random_element(elements=diagnosis),  # Diagnosis
        fake.random_element(elements=allergies),  # Allergies
        fake.random_element(elements=vitals),  # VitalSigns
        patient_id,  # PatientID (foreign key reference)
    )
    c.execute('INSERT INTO HealthRecords VALUES (?, ?, ?, ?, ?, ?)', health_records_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
