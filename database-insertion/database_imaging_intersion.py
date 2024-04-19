import sqlite3
from faker import Faker
from datetime import datetime, timedelta
import random 

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Initialize Faker
fake = Faker()

# Extract PatientIDs from the Patient table
c.execute('SELECT PatientID FROM Patient')
patient_ids = c.fetchall()

# List of different MRI abbreviations
mri_abbreviations = ['MRI', 'fMRI', 'DTI', 'MRA']
results = ["MRI reveals normal brain anatomy with no detectable abnormalities.",
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

# Function to generate a random datetime within the last 30 days
def random_datetime():
    return datetime.now() - timedelta(days=random.randint(1, 30))

# Insert data into ImagingData table with different MRI abbreviations
for i, (patient_id,) in enumerate(patient_ids):
    imaging_data = (
        f'ImagingID{i}',  # ImageID
        f'ImagingID{i}_'+patient_id+'.nii.gz',  # ImageFile
        fake.random_element(elements=['1.5T MRI', '3T MRI', 'Open MRI', 'Portable MRI']),  # MachineType
        fake.random_element(elements=mri_abbreviations),  # ModalityName (MRI abbreviations)
        fake.random_element(elements=results),  # Results
        random_datetime(),  # DataOfEntry
        fake.name(),  # Technician
        patient_id,  # PatientID (foreign key reference)
    )
    c.execute('INSERT INTO ImagingData VALUES (?, ?, ?, ?, ?, ?, ?, ?)', imaging_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
