import sqlite3
import random

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Input data
institution_names = ['Wake Forest University', 'Virginia Tech', 'University of Virginia', 'Georgia Tech', 'New York University']
cities = ['Winston-Salem', 'Blacksburg', 'Charlottesville', 'Atlanta', 'New York City']
fnames = ["John", "Jane", "Robert", "Emily", "Michael"]
lnames = ["Doe", "Smith", "Johnson", "Williams", "Brown"]
emails = ['john.doe@wakehealth.edu', 'jane.smith@vt.edu', 'robert.johnson@uva.edu', 'emily.williams@gt.edu', 'michael.brown@nyu.edu']

# Function to generate a random phone number
def random_phone_number():
    return f'{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}'

# Function to generate a random contact person name
def contact_person_name(fname,lname):
    return f'{fname} {lname}'

# Insert specific input data into ResearchInstitution table
for i, (institution_name, city, email,fname,lname) in enumerate(zip(institution_names, cities, emails,fnames,lnames)):
    institution_data = (
        f'Institution{i}',
        institution_name,
        city,
        email,
        random_phone_number(),
        contact_person_name(fname,lname),
    )
    c.execute('INSERT INTO ResearchInstitution VALUES (?, ?, ?, ?, ?, ?)', institution_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
