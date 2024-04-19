import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('/Users/swapster/Desktop/Database Management Systems/Project/neurogenix.db')
c = conn.cursor()

# Function to generate a random datetime within the last 30 days
def random_datetime():
    return datetime.now() - timedelta(days=random.randint(1, 30))

# Function to generate a random IP address
def random_ip_address():
    return f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}'

# Extract UserIDs from Users table
c.execute('SELECT UserID FROM Users')
user_ids = c.fetchall()

# Insert data into SecurityLogs table
for i in range(30):
    log_data = (
        f'LogID{i}',
        random_datetime(),
        random_ip_address(),
        random.choice(['Login', 'View', 'Update', 'Delete']),
        random.choice(user_ids)[0],
    )
    c.execute('INSERT INTO SecurityLogs VALUES (?, ?, ?, ?, ?)', log_data)

# Commit the changes and close the connection
conn.commit()
conn.close()
