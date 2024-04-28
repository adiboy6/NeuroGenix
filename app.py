import psycopg2
from psycopg2 import extras
from psycopg.rows import namedtuple_row, dict_row
from psycopg2.extras import NamedTupleCursor, DictCursor
from urllib.parse import urlparse
from faker import Faker
from datetime import date
from tqdm import tqdm
import json
from collections import OrderedDict
from flask import Flask, render_template, request, redirect, jsonify, url_for, jsonify
import pandas as pd
from datetime import datetime
import plotly.express as px
import base64
from io import BytesIO
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import string
import nltk
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


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

def fetch_data():
    # Connect to SQLite database
    conn = get_db_connection()

    # Query to join the tables and fetch required data
    query = """
    SELECT p.DOB, p.Gender, d.EducationLevel, d.Ethnicity, d.Occupation, d.MaritalStatus
    FROM Patient p
    JOIN Demographics d ON p.PatientID = d.PatientID
    """

    # Execute the query and load into DataFrame
    df = pd.read_sql_query(query, conn)
    print(df)
    # Calculate age from DOB
    df['DOB'] = pd.to_datetime(df['dob'])
    today = datetime.today()
    df['Age'] = df['DOB'].apply(lambda dob: (today.year - dob.year) - ((today.month, today.day) < (dob.month, dob.day)))

    # Close the connection
    conn.close()

    return df

# Function to create visualizations
def create_plots(df):
    # Age Boxplot
    fig_age = px.box(df, y='Age', title='Age Distribution', hover_data={'Age': True}, width=500, color_discrete_sequence=['#FDBCB4'])
    fig_age.update_layout(
    title={
        'text': 'Age Distribution',  # Title text
        'y':0.9,  # Title Y-position (top by default)
        'x':0.5,  # Title X-position (centering the title)
        'xanchor': 'center',  # Anchor title to center at X-position
        'yanchor': 'top'  # Anchor title to top at Y-position
    })
    fig_age.update_traces(hovertemplate='Age: %{y}')
    age_plot_html = fig_age.to_html(full_html=False)

    # Gender Pie Chart
    colors_gender = ['#FDBCB4', '#FFDAB9', '#B0E0E6']
    fig_gender = px.pie(df, names='gender', title='Gender Distribution', width=500)
    fig_gender.update_layout(
    title={
        'text': 'Gender Distribution',  # Title text
        'y':0.9,  # Title Y-position (top by default)
        'x':0.5,  # Title X-position (centering the title)
        'xanchor': 'center',  # Anchor title to center at X-position
        'yanchor': 'top'  # Anchor title to top at Y-position
    })
    fig_gender.update_traces(marker=dict(colors=colors_gender))
    gender_plot_html = fig_gender.to_html(full_html=False)

    # Marital Status Pie Chart
    colors_marital = ['#FDBCB4', '#FFDAB9', '#B0E0E6']
    fig_maritalstatus = px.pie(df, names='maritalstatus', title='Marital Status Distribution', 
                               labels={'MaritalStatus':'Marital Status'}, width=500,
                               color_discrete_sequence=colors_marital)
    fig_maritalstatus.update_layout(
    title={
        'text': 'Marital Status Distribution',  # Title text
        'y':0.9,  # Title Y-position (top by default)
        'x':0.5,  # Title X-position (centering the title)
        'xanchor': 'center',  # Anchor title to center at X-position
        'yanchor': 'top'  # Anchor title to top at Y-position
    })
    maritalstatus_plot_html = fig_maritalstatus.to_html(full_html=False)

    # This correction ensures the DataFrame columns are correctly named after resetting the index
    df_education = df['educationlevel'].value_counts().reset_index()
    df_education.columns = ['EducationLevel', 'Count']  # Naming columns explicitly
    colors_education = ['#FDBCB4', '#FFB6C1', '#B0E0E6', '#FFDAB9', '#8FBC8F']

    # Now, create the bar chart using these explicitly named columns
    fig_education = px.bar(df_education, x='EducationLevel', y='Count',
                        labels={'EducationLevel': 'Education Level', 'Count': 'Number of Patients'},
                        title='Education Level Distribution', width=500,
                        color='EducationLevel',
                        color_discrete_sequence=colors_education)
    fig_education.update_layout(
    title={
        'text': 'Education Distribution',  # Title text
        'y':0.9,  # Title Y-position (top by default)
        'x':0.5,  # Title X-position (centering the title)
        'xanchor': 'center',  # Anchor title to center at X-position
        'yanchor': 'top'  # Anchor title to top at Y-position
    })
    education_plot_html = fig_education.to_html(full_html=False)

    # This correction ensures the DataFrame columns are correctly named after resetting the index
    df_Ethnicity = df['ethnicity'].value_counts().reset_index()
    df_Ethnicity.columns = ['Ethnicity', 'Count']  # Naming columns explicitly
    colors_ethnicity = ['#FDBCB4', '#FFB6C1', '#B0E0E6', '#FFDAB9', '#8FBC8F']

    # Now, create the bar chart using these explicitly named columns
    fig_ethnicity = px.bar(df_Ethnicity, x='Ethnicity', y='Count',
                        labels={'Ethnicity': 'Ethnicity', 'Count': 'Number of Patients'},
                        color='Ethnicity',
                        title='Ethnicity Distribution', width=500,
                        color_discrete_sequence=colors_ethnicity)
    fig_ethnicity.update_layout(
    title={
        'text': 'Ethnicity Distribution',  # Title text
        'y':0.9,  # Title Y-position (top by default)
        'x':0.5,  # Title X-position (centering the title)
        'xanchor': 'center',  # Anchor title to center at X-position
        'yanchor': 'top'  # Anchor title to top at Y-position
    })
    ethnicity_plot_html = fig_ethnicity.to_html(full_html=False)

    # This correction ensures the DataFrame columns are correctly named after resetting the index
    df_occupation = df['occupation'].value_counts().reset_index()
    df_occupation.columns = ['Occupation', 'Count']  # Naming columns explicitly

    # Now, create the bar chart using these explicitly named columns
    fig_occupation = px.bar(df_occupation, x='Occupation', y='Count',
                        labels={'Occupation': 'Occupation', 'Count': 'Number of Patients'},
                        title='Occupation Distribution', width=500,
                        color='Occupation',
                        color_discrete_sequence=colors_ethnicity)
    fig_occupation.update_layout(
    title={
        'text': 'Occupation Distribution',  # Title text
        'y':0.9,  # Title Y-position (top by default)
        'x':0.5,  # Title X-position (centering the title)
        'xanchor': 'center',  # Anchor title to center at X-position
        'yanchor': 'top'  # Anchor title to top at Y-position
    })
    occupation_plot_html = fig_occupation.to_html(full_html=False)

    return age_plot_html, gender_plot_html, education_plot_html, ethnicity_plot_html, occupation_plot_html, maritalstatus_plot_html

def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove stop words
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

def fetch_text_data_and_generate_word_clouds():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)

    # Fetch data from HealthRecords
    cursor.execute("SELECT Medications, Diagnosis, Allergies, VitalSigns FROM HealthRecords")
    text_data = cursor.fetchall()
    # Concatenate all text data for simplicity; you might want to handle them separately
    medications_text = []
    diagnosis_text = []
    allergies_text = []
    vitalsigns_text = []
    for row in text_data:
        medications_text.append(str(row[0]))
        diagnosis_text.append(str(row[1]))
        allergies_text.append(str(row[2]))
        vitalsigns_text.append(str(row[3]))
    medications_combined = " ".join(medications_text)
    diagnosis_combined = " ".join(diagnosis_text)
    allergies_combined = " ".join(allergies_text)
    vitalsigns_combined = " ".join(vitalsigns_text)
    medications_combined = preprocess_text(medications_combined)
    diagnosis_combined = preprocess_text(diagnosis_combined)
    allergies_combined = preprocess_text(allergies_combined)
    vitalsigns_combined = preprocess_text(vitalsigns_combined)


    # Fetch data from ImagingData
    cursor.execute("SELECT Results FROM ImagingData")
    imaging_data = cursor.fetchall()
    imaging_text = " ".join([row[0] for row in imaging_data])
    imaging_text = preprocess_text(imaging_text)

    conn.close()

    # Generate word clouds
    wordcloud1 = generate_word_cloud(medications_combined, "Medications Word Cloud")
    wordcloud2 = generate_word_cloud(diagnosis_combined, "Diagnosis Word Cloud")
    wordcloud3 = generate_word_cloud(allergies_combined, "Allergies Word Cloud")
    wordcloud4 = generate_word_cloud(vitalsigns_combined, "Vital Signs Word Cloud")
    wordcloud5 = generate_word_cloud(imaging_text, "Imaging Results Word Cloud")

    return wordcloud1, wordcloud2, wordcloud3, wordcloud4, wordcloud5

# Function to generate a word cloud from text
def generate_word_cloud(text, title):
    wordcloud = WordCloud(width=800, height=400, background_color ='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(title, fontsize=18, color='black')
    # Save the plot as a byte array
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    # Encode the image in base64 to embed in HTML
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"

###############################################
######                  HOME             ######
###############################################
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
    df = fetch_data()
    age_plot, gender_plot, education_plot, ethnicity_plot, occupation_plot, maritalstatus_plot = create_plots(df)
    wordcloud1, wordcloud2, wordcloud3, wordcloud4, wordcloud5 = fetch_text_data_and_generate_word_clouds()
    usertype = request.args.get('usertype')
    button_options = ['Show', 'Insert', 'Update', 'Delete']
    if usertype=='Admin':
        # return render_template('home.html', len=len(table_names), table_names=table_names, usertype=usertype, button_options=button_options)
        return render_template('home.html',
                            age_plot=age_plot,
                            gender_plot=gender_plot,
                            education_plot=education_plot,
                            ethnicity_plot=ethnicity_plot,
                            occupation_plot=occupation_plot,
                            maritalstatus_plot=maritalstatus_plot,
                            wordcloud1=wordcloud1,
                            wordcloud2=wordcloud2,
                            wordcloud3=wordcloud3,
                            wordcloud4=wordcloud4,
                            wordcloud5=wordcloud5)
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


###############################################
######                  APIs             ######
###############################################
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
def get_table_schema(tname=None, label=True):
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
    if not label : return schema
    f = open('table_schema.json', 'r')
    tableSchemaJson = json.load(f)
    schema_label = OrderedDict()
    for i in schema:
        key = i[0]
        schema_label[key]= tableSchemaJson[key]
    cursor.close()
    if tname == None:
        return json.dumps(schema_label)
    return schema_label
    
@app.route('/getPrimaryKeyValues', methods=['GET'])
def get_primary_key_and_values():
    table_name = request.args.get('tableName')
    primary_key = request.args.get('primaryKey')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Retrieve the primary key column name using information_schema
    
    # Retrieve primary key values from the table
    values_query = f"SELECT {primary_key} FROM {table_name}"
    cursor.execute(values_query)
    primary_key_values = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return json.dumps(primary_key_values)

@app.route('/getRowData', methods=['GET'])
def get_row():
    table_name = request.args.get('table')
    primary_key = request.args.get('primary_key')
    if not table_name or not primary_key:
        return jsonify({"error": "Missing table name or primary key"}), 400
    
    schema = get_table_schema(table_name, label=False)
    primary_key_name = schema[0][0]  # Adjusted to match PostgreSQL's output
    conn = get_db_connection()
    curr = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = f"SELECT * FROM {table_name} WHERE {primary_key_name} = %s"
    curr.execute(query, (primary_key,))
    row = curr.fetchone()
    conn.close()
    
    if row:
        # Convert the row into a dict to jsonify it
        return row
    else:
        return jsonify({"error": "Row not found"}), 404

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

    schema = get_table_schema(table_name, label=False)
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
        return jsonify({"success": True, "message": f"Record updated into {table_name} successfully."})
    except psycopg2.Error as e:
        return jsonify({"success": False, "message": f"Error updating into {table_name}: {e}"})
    
@app.route('/postData', methods=['POST'])
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
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "No table specified"})


@app.route('/deleteData', methods=['POST'])
def delete():
    print("here")
    table_name = request.args.get('table')
    schema = get_table_schema(table_name, label=False)
    primary_key_name = schema[0][0]  # Assuming first column is the primary key
    if not table_name:
        return jsonify({"error": "No table specified"}), 400

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
            return jsonify({"message": f"Record in {table_name} deleted successfully."}), 200
        except psycopg2.Error as e:
            return jsonify({"error": f"Error deleting {table_name}: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
