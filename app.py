import psycopg2
from psycopg2 import extras
from urllib.parse import urlparse
from faker import Faker
from datetime import date
from tqdm import tqdm
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

def get_db_connection():
    pg_uri = "postgres://ghsqoqpo:FjAUwUOm5UN2Rg4DoZ3bpnj6O-5eb2pV@isilo.db.elephantsql.com/ghsqoqpo"
    # conStr = "localhost://username:password@data_quality:5432"
    result = urlparse(pg_uri)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    connection = psycopg2.connect(
        database = database,
        user = username,
        password = password,
        host = hostname,
        port = port
    )
    return connection;

def get_table_names():
    conn = get_db_connection()
    conn = conn.cursor()
    conn.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';""")
    tables_names = [i[0] for i in conn.fetchall()]
    conn.close()
    return tables_names

def get_table_schema(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"PRAGMA table_info({table_name})"
    cursor.execute(query)
    schema = cursor.fetchall()
    cursor.close()
    return schema

def get_primary_key_and_values(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Assuming the first column is always the primary key, adjust accordingly
    primary_key_query = f"PRAGMA table_info({table_name})"
    cursor.execute(primary_key_query)
    primary_key = cursor.fetchall()[0][1]  # Adjust based on your table schema

    values_query = f"SELECT {primary_key} FROM {table_name}"
    cursor.execute(values_query)
    primary_key_values = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return primary_key, primary_key_values

@app.route('/get-row', methods=['GET'])
def get_row():
    table_name = request.args.get('table')
    primary_key = request.args.get('primary_key')
    if not table_name or not primary_key:
        return jsonify({"error": "Missing table name or primary key"}), 400
    
    schema = get_table_schema(table_name)
    primary_key_name = schema[0][1]  # Assuming first column is the primary key
    
    conn = get_db_connection()
    conn.row_factory = extras.NamedTupleCursor
    query = f"SELECT * FROM {table_name} WHERE {primary_key_name} = ?"
    row = conn.execute(query, (primary_key,)).fetchone()
    conn.close()
    
    if row:
        # Convert the row into a dict to jsonify it
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Row not found"}), 404


@app.route('/')
def home():
    table_names = get_table_names()
    return render_template('home.html', len = len(table_names), table_names = table_names)

@app.route('/show')
def show():
    table_name = request.args.get('table')
    if table_name:
        conn = get_db_connection()
        conn.row_factory = extras.NamedTupleCursor
        query = f"SELECT * FROM {table_name}"
        try:
            data = conn.execute(query).fetchall()
        except psycopg2.Error as e:
            data = []
            print(f"Error fetching data from {table_name}: {e}")
        conn.close()
    else:
        data = []
    return render_template('show.html', data=data, table_name=table_name)

@app.route('/login')
def verify():
    table_name = request.args.get('table')
    if table_name:
        conn = get_db_connection()
        conn.row_factory = extras.NamedTupleCursor
        query = f"SELECT * FROM Users where UserType={usertype} and UserName={username} and password={password}"
        try:
            data = conn.execute(query).fetchall()
        except psycopg2.Error as e:
            data = []
            print(f"User not found/User id incorrect/Password incorrect")
        conn.close()
    else:
        data = []
    return render_template('login.html', data=data, table_name=table_name)

@app.route('/update', methods=['GET', 'POST'])
def update():
    table_name = request.args.get('table')
    if not table_name:
        return "No table specified"

    if request.method == 'POST':
        schema = get_table_schema(table_name)
        primary_key_name = schema[0][1]
        # Handle form submission for updating the record
        # Fetch the primary key and updated values from the form
        primary_key = request.form['primary_key']
        updated_values = {col: request.form[col] for col in request.form if col != 'primary_key'}
        
        # Construct the UPDATE query dynamically
        set_clause = ', '.join([f"{col} = ?" for col in updated_values])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_name} = ?"
        
        try:
            conn = get_db_connection()
            conn.execute(query, list(updated_values.values()) + [primary_key])
            conn.commit()
            conn.close()
            return f"Record in {table_name} updated successfully."
        except psycopg2.Error as e:
            return f"Error updating {table_name}: {e}"
    else:
        # For GET request, display the update form
        schema = get_table_schema(table_name)
        primary_key_name = schema[0][1]  # Assuming first column is the primary key
        # Fetch primary key values for the dropdown
        conn = get_db_connection()
        conn.row_factory = extras.NamedTupleCursor
        primary_keys = conn.execute(f"SELECT {primary_key_name} FROM {table_name}").fetchall()
        conn.close()
        
        return render_template('update.html', schema=schema, table_name=table_name, primary_keys=primary_keys, primary_key_name=primary_key_name)

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    table_name = request.args.get('table')
    if table_name:
        schema = get_table_schema(table_name)
        if request.method == 'POST':
            # Construct the INSERT INTO query dynamically
            columns = ', '.join([col[1] for col in schema])  # col[1] is the column name in the schema
            placeholders = ', '.join(['?' for _ in schema])
            values = [request.form[col[1]] for col in schema]
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            try:
                conn = get_db_connection()
                conn.execute(query, values)
                conn.commit()
                conn.close()
                return f"Record inserted into {table_name} successfully."
            except psycopg2.Error as e:
                return f"Error inserting into {table_name}: {e}"
        else:
            special_fields = {
                'Gender': ['Male', 'Female', 'Other'],
                'Password' : None,
                'DOB': None,
                'DataOfEntry': None
                # Other special fields can be added here
            }
            # GET request, show the form
            return render_template('insert.html', schema=schema, table_name=table_name, special_fields=special_fields)
    else:
        return "No table specified"

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    table_name = request.args.get('table')
    if not table_name:
        return "No table specified"

    if request.method == 'POST':
        primary_key = request.form['primary_key']
        schema = get_table_schema(table_name)
        primary_key_name = schema[0][1]  # Assuming first column is the primary key
        
        try:
            conn = get_db_connection()
            query = f"DELETE FROM {table_name} WHERE {primary_key_name} = ?"
            conn.execute(query, (primary_key,))
            conn.commit()
            conn.close()
            # Redirect or inform the user of successful deletion
            return f"Record in {table_name} deleted successfully."
        except psycopg2.Error as e:
            return f"Error deleting {table_name}: {e}"
    else:
        # For GET request, display the delete form
        conn = get_db_connection()
        schema = get_table_schema(table_name)
        primary_key_name = schema[0][1]  # Assuming first column is the primary key
        conn.row_factory = psycopg2
        primary_keys = conn.execute(f"SELECT {primary_key_name} FROM {table_name}").fetchall()
        conn.close()
        return render_template('delete.html', table_name=table_name, primary_keys=primary_keys, primary_key_name=primary_key_name)

if __name__ == '__main__':
    app.run(port=6000, debug=True)
