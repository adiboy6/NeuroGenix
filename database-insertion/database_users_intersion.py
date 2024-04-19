import sqlite3
import random
import string
from faker import Faker

fake = Faker()

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Function to generate a random phone number
def random_phone_number():
    return f'{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}'

# Function to generate a random username
def generate_username(first_name, last_name):
    return f'{first_name.lower()}_{last_name.lower()}'

# Function to generate a random password
def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(12))  # Adjust the length as needed

# Insert data into Users table
for i in range(30):
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = generate_username(first_name, last_name)
    password = generate_password()
    user_data = (
        f'UserID{i}',
        random.choice(['Admin', 'Professor', 'Researcher', 'Clinician', 'Guest']),
        first_name,
        last_name,
        username,
        password,
        f'Institution{i}',
    )
    c.execute('INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?)', user_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
