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

# Insert data into Demographics table
for i, (patient_id,) in enumerate(patient_ids):
    demographics_data = (
        f'DemographicID{i}',  # DemographicsID
        fake.random_element(elements=('High School', 'College', 'Bachelor', 'Master', 'Doctorate')),  # EducationLevel
        fake.random_element(elements=('Caucasian', 'African American', 'Asian', 'Hispanic', 'Other')),  # Ethnicity
        fake.random_element(elements=('Engineer', 'Teacher', 'Doctor', 'Sales', 'Other')),  # Occupation
        fake.random_element(elements=('Single', 'Married', 'Divorced')),  # MaritalStatus
        patient_id,  # PatientID (foreign key reference)
    )
    c.execute('INSERT INTO Demographics VALUES (?, ?, ?, ?, ?, ?)', demographics_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
