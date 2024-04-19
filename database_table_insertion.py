import sqlite3
from faker import Faker
import string
import random
from datetime import date
import re
from tqdm import tqdm

connection = sqlite3.connect('./neurogenix.db')
c = connection.cursor()

fake = Faker()  

def pwd_generator(size=8, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits + "._-#@!"):
    return ''.join(random.choice(chars) for _ in range(random.randint(0,8)))

def generate_valid_password():
    while True:
        password = fake.password(length=8, special_chars=True, digits=False, upper_case=True, lower_case=True)
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(not c.isalnum() for c in password) and
            len(password) >= 8):
            return password

def insert_values():
    for _ in tqdm(range(100)):
        patient_id = fake.uuid4()[:25]
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
        gender = random.choice(['Male', 'Female', 'Other'])
        address = fake.address()
        phone_number = random.randint(10**9, (10**10) - 1)
        email = fake.email()

        c.execute('''
            INSERT INTO Patient (PatientID, FName, LName, DOB, Gender, Address, PhoneNumber, Email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, first_name, last_name, dob, gender, address, phone_number, email))

        user_id = fake.uuid4()[:25]
        user_type = random.choice(['Admin', 'Professor', 'Researcher', 'Clinician', 'Guest'])
        fname = fake.first_name()
        lname = fake.last_name()
        username = fake.user_name()[:15]
        password = pwd_generator()
        institution_id = fake.uuid4()[:25]
        try:
            c.execute('''
                INSERT INTO Users (UserID, UserType, FName, LName, UserName, Password, InstitutionID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_type, fname, lname, username, password, institution_id))
            print("Successfully " + password)
        except Exception as  e:
            pass
        
    connection.commit()

insert_values()