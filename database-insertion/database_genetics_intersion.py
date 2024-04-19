import sqlite3
from faker import Faker
import random

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Extract PatientIDs from the Patient table
c.execute("SELECT PatientID FROM Patient")
patient_ids = c.fetchall()

# Initialize Faker
fake = Faker()

def generate_random_sequence(length):
    bases = ['A', 'T', 'C', 'G']
    random_sequence = ''.join(random.choice(bases) for _ in range(length))
    return random_sequence

# Insert data into GenomicData table
for i,(patient_id,) in enumerate(patient_ids):
    genomic_data = (
        f'GenomicID{i}',  # GenomicID
        f'GenomicID{i}_Expression.csv',  # GeneExpression
        'BDNF',  # GeneticMarkers
        generate_random_sequence(12),  # DNASequence
        patient_id,  # PatientID (foreign key reference)
    )
    c.execute('INSERT INTO GenomicData VALUES (?, ?, ?, ?, ?)', genomic_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
