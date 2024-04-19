import sqlite3
connection = sqlite3.connect('./neurogenix.db')
c = connection.cursor()

def create_table():
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS Patient (
        PatientID TEXT PRIMARY KEY CHECK(length(PatientID) <= 25),
        FName TEXT CHECK(length(FName) <= 15),
        LName TEXT CHECK(length(LName) <= 15),
        DOB DATE,
        Gender TEXT CHECK(Gender IN ('Male', 'Female', 'Other')),
        Address TEXT,
        PhoneNumber TEXT CHECK(length(PhoneNumber) == 10),
        Email TEXT CHECK(Email LIKE '%@%' AND Email LIKE '%.%')
        )
        '''
        )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS GenomicData (
        GenomicID TEXT PRIMARY KEY CHECK(length(GenomicID) <= 25),
        GeneExpression TEXT,
        GeneticMarkers TEXT,
        DNASequence TEXT,
        PatientID TEXT REFERENCES Patient(PatientID) ON DELETE CASCADE
        )
        '''
        )
    c.execute(
       '''
        CREATE TABLE IF NOT EXISTS ImagingData (
        ImageID TEXT PRIMARY KEY CHECK(length(ImageID) <= 25),
        ImageFile TEXT,
        MachineType TEXT,
        ModalityName TEXT,
        Results TEXT,
        DataOfEntry DATE,
        Technician TEXT,
        PatientID TEXT REFERENCES Patient(PatientID) ON DELETE CASCADE
        )
       '''
       )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS HealthRecords (
        RecordID TEXT PRIMARY KEY CHECK(length(RecordID) <= 25),
        Medications TEXT,
        Diagnosis TEXT,
        Allergies TEXT,
        VitalSigns TEXT,
        PatientID TEXT REFERENCES Patient(PatientID) ON DELETE CASCADE
        )
        '''
        )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS Demographics (
        DemographicsID TEXT PRIMARY KEY CHECK(length(DemographicsID) <= 25),
        EducationLevel TEXT,
        Ethnicity TEXT,
        Occupation TEXT,
        MaritalStatus TEXT CHECK(MaritalStatus IN ('Single', 'Married', 'Divorced')),
        PatientID TEXT REFERENCES Patient(PatientID) ON DELETE CASCADE
        )
        '''
        )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS Users (
        UserID TEXT PRIMARY KEY CHECK(length(UserID) <= 25),
        UserType TEXT,
        FName TEXT CHECK(length(FName) <= 15),
        LName TEXT CHECK(length(LName) <= 15),
        UserName TEXT CHECK(length(UserName) <= 15),
        Password TEXT CHECK(length(Password) >= 8 LIKE '^(?=.[0-9])(?=.[a-z])(?=.[A-Z])(?=.[._-#@!]).+$'),
        InstitutionID TEXT REFERENCES ResearchInstitution(InstitutionID) ON DELETE CASCADE
        )
        '''
        )
    # Password TEXT CHECK(length(Password) >= 8 AND Password LIKE '%[a-z]%' AND Password LIKE '%[A-Z]%' AND Password LIKE '%[0-9]%' AND Password LIKE '%[^a-zA-Z0-9]%'),
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS ResearchInstitution (
        InstitutionID TEXT PRIMARY KEY CHECK(length(InstitutionID) <= 25),
        InstitutionName TEXT,
        Location TEXT,
        Email TEXT CHECK(Email LIKE '%@%.%' AND length(Email) > 5),
        PhNo TEXT CHECK(length(PhNo) == 10),
        ContactPerson TEXT
        )
        '''
        )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS SecurityLogs (
        LogID TEXT PRIMARY KEY CHECK(length(LogID) <= 25),
        LogDateTime TIMESTAMP,
        IPAddress TEXT CHECK(IPAddress LIKE '%.%.%.%'),
        ActionPerformed TEXT,
        UserID TEXT REFERENCES Users(UserID) ON DELETE CASCADE
        )
        '''
        )
    
    connection.commit()

create_table()