import psycopg2
from psycopg2 import extras
from psycopg.rows import namedtuple_row, dict_row
from psycopg2.extras import NamedTupleCursor, DictCursor
from urllib.parse import urlparse
from faker import Faker
from datetime import date
from tqdm import tqdm
import json
from flask import Flask, render_template, request, redirect, jsonify, url_for, jsonify


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

@app.route('/getTableNames', methods=['GET'])
def get_table_names():
    conn = get_db_connection()
    conn = conn.cursor()
    conn.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';""")
    tables_names = [i[0] for i in conn.fetchall()]
    conn.close()
    return jsonify(tables_names)

@app.route('/getTableNamesLabels', methods=['GET'])
def get_table_names_labels():
    f = open('table_names.json', 'r')
    return jsonify(f.read())

@app.route('/getTableSchema', methods=['GET'])
def get_table_schema(tname=None):
    if tname == None:
        table_name = request.args.get('tableName')
    else:
        table_name = tname
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"""SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
    """
    cursor.execute(query)
    schema = cursor.fetchall()
    f = open('table_schema.json', 'r')
    tableSchemaJson = json.load(f)
    schema_label = dict()
    for i in schema:
        key = i[0]
        schema_label[key]= tableSchemaJson[key]
    cursor.close()
    if tname == None:
        return jsonify(schema_label)
    return schema_label

def get_primary_key_and_values(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Retrieve the primary key column name using information_schema
    primary_key_query = f"""SELECT column_name
                              FROM information_schema.key_column_usage
                              WHERE table_name = '{table_name}'"""
    cursor.execute(primary_key_query)
    primary_key_name = cursor.fetchone()[0]
    
    # Retrieve primary key values from the table
    values_query = f"SELECT {primary_key_name} FROM {table_name}"
    cursor.execute(values_query)
    primary_key_values = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return primary_key_name, primary_key_values

@app.route('/rowData', methods=['GET'])
def get_row():
    table_name = request.args.get('table')
    primary_key = request.args.get('primary_key')
    if not table_name or not primary_key:
        return jsonify({"error": "Missing table name or primary key"}), 400
    
    schema = get_table_schema(table_name)
    primary_key_name = schema[0][0]  # Adjusted to match PostgreSQL's output
    
    conn = get_db_connection()
    curr = conn.cursor(cursor_factory=NamedTupleCursor)
    query = f"SELECT * FROM {table_name} WHERE {primary_key_name} = %s"
    row = curr.execute(query, (primary_key,)).fetchone()
    conn.close()
    
    if row:
        # Convert the row into a dict to jsonify it
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Row not found"}), 404

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        usertype = request.form.get('usertype')

        # Perform authentication (e.g., check username and password against a database)
        if authenticate(username, password, usertype):
            # Authentication successful, redirect to home page or some other authenticated route
            return redirect(url_for('home', usertype=usertype))
    else:
        # Authentication failed, render login page with an error message
        return render_template('login.html', error='Invalid credentials')

def authenticate(username, password, usertype):
    conn = get_db_connection()
    curr = conn.cursor()
    query = f"SELECT * FROM Users where UserType=\'{usertype}\' and UserName=\'{username}\' and password=\'{password}\'"
    try:
        curr.execute(query)
        data = curr.fetchone()
        if data is None:
            raise psycopg2.Error
        return True
    except psycopg2.Error as e:
        data = []
        print(f"User not found/User id incorrect/Password incorrect")
    conn.close()

@app.route('/home')
def home():
    usertype = request.args.get('usertype')
    button_options = ['Show', 'Insert', 'Update', 'Delete']
    if usertype=='Admin':
        # return render_template('home.html', len=len(table_names), table_names=table_names, usertype=usertype, button_options=button_options)
        return render_template('home.html')
    elif usertype=='Professor':
        button_options.remove('Insert')
        return render_template('home.html', len=len(table_names), table_names=table_names, usertype=usertype, button_options=button_options)
    elif usertype=='Guest':
        table_names.remove('researchinstitution')
        table_names.remove('users')
        table_names.remove('securitylogs')
        button_options = ['Show']
        return render_template('home.html', len=len(table_names), table_names=table_names, usertype=usertype, button_options=button_options)
    elif usertype=='Researcher' or usertype=='Clinnician':
        table_names.remove('users')
        table_names.remove('securitylogs')
        return render_template('home.html', len=len(table_names), table_names=table_names, usertype=usertype, button_options=button_options)
    else:
        return redirect('/')


@app.route('/show')
def show():
    table_name = request.args.get('table')
    if table_name:
        conn = get_db_connection()
        curr = conn.cursor(cursor_factory=DictCursor)  # Set cursor to return dictionary
        query = f"SELECT * FROM {table_name} LIMIT 100"
        try:
            curr.execute(query)
            data = curr.fetchall()
        except psycopg2.Error as e:
            data = []
            print(f"Error fetching data from {table_name}: {e}")
        conn.close()
    else:
        data = []
    return render_template('show.html', data=data, table_name=table_name)

@app.route('/getTableData', methods=['GET'])
def get_table_data():
    table_name = request.args.get('table')
    if table_name:
        conn = get_db_connection()
        curr = conn.cursor(cursor_factory=DictCursor)  # Set cursor to return dictionary
        query = f"SELECT * FROM {table_name} LIMIT 100"
        try:
            curr.execute(query)
            data = curr.fetchall()
            
            # Get column names
            column_names = [desc[0] for desc in curr.description]

            # Convert data to key-value format
            key_value_data = []
            for row in data:
                key_value_row = {}
                for col_name, value in zip(column_names, row):
                    key_value_row[col_name] = value
                key_value_data.append(key_value_row)
        except psycopg2.Error as e:
            key_value_data = []
            print(f"Error fetching data from {table_name}: {e}")
        conn.close()
    else:
        key_value_data = []
    return jsonify(key_value_data)

@app.route('/update', methods=['GET', 'POST'])
def update():
    table_name = request.args.get('table')
    if not table_name:
        return "No table specified"

    if request.method == 'POST':
        schema = get_table_schema(table_name)
        primary_key_name = schema[0][0]
        # Handle form submission for updating the record
        primary_key = request.form['primary_key']
        updated_values = {col[0]: request.form[col[0]] for col in schema if col[0] != primary_key_name}

        # Construct the UPDATE query dynamically
        set_clause = ', '.join([f"{col} = %s" for col in updated_values])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key_name} = %s"
        values = list(updated_values.values()) + [primary_key]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            return f"Record in {table_name} updated successfully."
        except psycopg2.Error as e:
            return f"Error updating {table_name}: {e}"
    else:
        # For GET request, display the update form
        schema = get_table_schema(table_name)
        primary_key_name = schema[0][0]  # Assuming first column is the primary key
        # Fetch primary key values for the dropdown
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(f"SELECT {primary_key_name} FROM {table_name}")
        primary_keys = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('update.html', schema=schema, table_name=table_name, primary_keys=primary_keys, primary_key_name=primary_key_name)

@app.route('/insert', methods=['POST'])
def insert():
    table_name = request.args.get('table')
    if table_name:
        schema = get_table_schema(table_name)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Construct the INSERT INTO query dynamically
            columns = ', '.join([col for col in schema])  # col[0] is the column name in the schema
            placeholders = ', '.join(['%s' for _ in schema])
            values = [request.form[col] for col in schema]
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, values)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return jsonify({"success": True, "message": f"Record inserted into {table_name} successfully."})
        except psycopg2.Error as e:
            return jsonify({"success": False, "message": f"Error inserting into {table_name}: {e}"})
    
    else:
        return jsonify({"success": False, "message": "No table specified"})


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    table_name = request.args.get('table')
    schema = get_table_schema(table_name)
    primary_key_name = schema[0][0]  # Assuming first column is the primary key
    if not table_name:
        return "No table specified"

    if request.method == 'POST':
        primary_key = request.form['primary_key']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = f"DELETE FROM {table_name} WHERE {primary_key_name} = %s"
            cursor.execute(query, (primary_key,))
            conn.commit()
            cursor.close()
            conn.close()
            return f"Record in {table_name} deleted successfully."
        except psycopg2.Error as e:
            return f"Error deleting {table_name}: {e}"
    else:
        # For GET request, display the delete form
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(f"SELECT {primary_key_name} FROM {table_name}")
        primary_keys = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('delete.html', table_name=table_name, primary_keys=primary_keys, primary_key_name=primary_key_name)  

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
