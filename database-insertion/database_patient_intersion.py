import sqlite3
from faker import Faker
import random

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Initialize Faker
fake = Faker()

def random_phone_number():
    return f'{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}'

# Generate and insert 30 sets of random patient data into the Patient table
for i in range(30):
    patient_data = (
        f'PatientID{i}',  # PatientID
        fake.first_name(),  # FName
        fake.last_name(),  # LName
        fake.date_of_birth(minimum_age=18, maximum_age=80),  # DOB
        fake.random_element(elements=('Male', 'Female', 'Other')),  # Gender
        fake.address(),  # Address
        random_phone_number(),  # PhoneNumber
        fake.email(),  # Email
    )
    c.execute('INSERT INTO Patient VALUES (?, ?, ?, ?, ?, ?, ?, ?)', patient_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
