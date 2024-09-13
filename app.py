import streamlit as st
import snowflake.connector
import speech_recognition as sr
import pandas as pd
import speech_recognition as sr
import pyttsx3 

# Snowflake connection setup
def snowflake_connect():
    conn = snowflake.connector.connect(
        user='SRIKS',
        password='Srik@2005',
        account='okvuykz-mb80577',
        warehouse='COMPUTE_WH',
        database='med',
        schema='Therapy',
        role='ACCOUNTADMIN'
    )
    return conn

# Function to fetch data from Snowflake
def fetch_data(query):
    conn = snowflake_connect()
    cur = conn.cursor()
    try:
        cur.execute(query)
        data = cur.fetchall()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        data = []
    finally:
        conn.close()
    return data

# Function to add new patient profile
def add_patient_profile(name, age, medical_history, therapy_goals):
    conn = snowflake_connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO patient_profiles (name, age, medical_history, therapy_goals) VALUES (%s, %s, %s, %s)", 
                    (name, age, medical_history, therapy_goals))
        conn.commit()
        st.success("Patient added successfully!")
    except Exception as e:
        st.error(f"Error adding patient profile: {e}")
    finally:
        conn.close()

# Function to track patient progress
def track_patient_progress(patient_id):
    query = f"SELECT session_date, progress_metric FROM patient_progress WHERE patient_id = {patient_id}"
    data = fetch_data(query)
    if not data:
        st.warning("No data found for this patient ID.")
    else:
        df = pd.DataFrame(data, columns=['Session Date', 'Progress Metric'])
        st.write(df)  # Display raw data for debugging
        if not df.empty:
            df['Session Date'] = pd.to_datetime(df['Session Date'])
            df.set_index('Session Date', inplace=True)

# Function to add therapist profile
def add_therapist_profile(name, specialty, availability):
    conn = snowflake_connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO therapist_profiles (name, specialty, availability) VALUES (%s, %s, %s)", 
                    (name, specialty, availability))
        conn.commit()
        st.success("Therapist added successfully!")
    except Exception as e:
        st.error(f"Error adding therapist profile: {e}")
    finally:
        conn.close()

# Function for scheduling and allocation
def schedule_patient(patient_id, therapist_id):
    conn = snowflake_connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO schedule (patient_id, therapist_id) VALUES (%s, %s)", (patient_id, therapist_id))
        conn.commit()
        st.success("Patient scheduled successfully!")
    except Exception as e:
        st.error(f"Error scheduling patient: {e}")
    finally:
        conn.close()

# Speech-to-Text session notes
def record_session():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use microphone as source
    with sr.Microphone() as source:
        st.write("Please speak something...")  # Display instructions on Streamlit

        # Listen for the user's input
        audio = recognizer.listen(source)

        try:
            # Use Google's speech recognition to convert to text
            text = recognizer.recognize_google(audio)
            st.write("You said: " + text)  # Display recognized text on Streamlit
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio")
        except sr.RequestError:
            st.write("Could not request results from the speech recognition service")


# Streamlit interface
st.title("Therapy Management System")

menu = st.sidebar.selectbox("Menu", ["Patient Profiles", "Therapist Management", "Session Logging"])

if menu == "Patient Profiles":
    st.header("Patient Profiles")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    medical_history = st.text_area("Medical History")
    therapy_goals = st.text_area("Therapy Goals")
    if st.button("Add Patient"):
        add_patient_profile(name, age, medical_history, therapy_goals)

    patient_id = st.number_input("Enter Patient ID to Track Progress", min_value=1)
    if st.button("Track Progress"):
        track_patient_progress(patient_id)

elif menu == "Therapist Management":
    st.header("Therapist Management")
    name = st.text_input("Therapist Name")
    specialty = st.text_input("Specialty")
    availability = st.text_input("Availability")
    if st.button("Add Therapist"):
        add_therapist_profile(name, specialty, availability)

    patient_id = st.number_input("Patient ID", min_value=1)
    therapist_id = st.number_input("Therapist ID", min_value=1)
    if st.button("Schedule Patient"):
        schedule_patient(patient_id, therapist_id)

elif menu == "Session Logging":
    st.header("Session Logging")
    if st.button("Start Recording"):
        record_session()
