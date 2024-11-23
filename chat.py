import openai
import streamlit as st
import sqlite3
import os
import speech_recognition as sr
from dotenv import load_dotenv
from datetime import datetime
# Load environment variables (API keys)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Initialize recognizer for voice input
recognizer = sr.Recognizer()
# Database initialization
def init_db():
    conn = sqlite3.connect('student_assistant.db')
    c = conn.cursor()
    # Create the necessary tables
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        selected_subjects TEXT NOT NULL
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES user_profiles(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY,
        subject_name TEXT NOT NULL UNIQUE
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS student_dashboard (
        username TEXT PRIMARY KEY,
        selected_subjects TEXT,
        chat_sessions INTEGER DEFAULT 0,
        pdf_processed INTEGER DEFAULT 0,
        urls_explored INTEGER DEFAULT 0
    )''')

    conn.commit()
    conn.close()

def insert_initial_subjects():
    subjects = [
        "Data Science", "Computer Networks", "Operating Systems", "Java", "Machine Learning",
        "C++", "Automata Theory", "Python", "Statistics", "NLP"
    ]

    conn = sqlite3.connect('student_assistant.db')
    c = conn.cursor()
    for subject in subjects:
        c.execute("INSERT OR IGNORE INTO subjects (subject_name) VALUES (?)", (subject,))
    conn.commit()
    conn.close()

def fetch_subjects():
    conn = sqlite3.connect('student_assistant.db')
    c = conn.cursor()
    c.execute("SELECT subject_name FROM subjects")
    subjects = [row[0] for row in c.fetchall()]
    conn.close()
    return subjects

# Function to log chat activity
def log_chat_activity(username, interaction_type):
    conn = sqlite3.connect('student_assistant.db')
    c = conn.cursor()

    if interaction_type == "chat":
        c.execute("UPDATE student_dashboard SET chat_sessions = chat_sessions + 1 WHERE username = ?", (username,))
    elif interaction_type == "pdf":
        c.execute("UPDATE student_dashboard SET pdf_processed = pdf_processed + 1 WHERE username = ?", (username,))
    elif interaction_type == "url":
        c.execute("UPDATE student_dashboard SET urls_explored = urls_explored + 1 WHERE username = ?", (username,))

    conn.commit()
    conn.close()

# Function to handle chatbot interaction
def chatbot_interaction(prompt, username):
    # Log chat activity
    log_chat_activity(username, "chat")

    # Fetch chatbot response
    assistant_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )['choices'][0]['message']['content']

    return assistant_response

# Voice input function
def get_voice_input():
    try:
        with sr.Microphone() as source:
            st.write("Listening... Speak now.")
            audio = recognizer.listen(source, timeout=5)
            st.write("Processing your voice input...")
            voice_text = recognizer.recognize_google(audio)
            return voice_text
    except sr.UnknownValueError:
        return "Sorry, I could not understand your voice."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# Initialize Streamlit app
st.title("Student Assistant")

# Initialize the database
init_db()
insert_initial_subjects()

# Fetch subjects from the database
available_subjects = fetch_subjects()

# Initialize session variables if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# User selects subjects
selected_subjects = st.sidebar.multiselect("Select Subjects:", available_subjects)

# Display chat history
if selected_subjects:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Option to choose text input or voice input
    input_method = st.radio("Choose input method", ["Text", "Voice"])

    if input_method == "Text":
        # Text input
        if prompt := st.chat_input("Ask a question related to selected subjects"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate chatbot response
            assistant_response = chatbot_interaction(prompt, st.session_state.get("username", "unknown_user"))
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    elif input_method == "Voice":
        # Voice input
        if st.button("Record Voice Input 🎙️"):
            voice_text = get_voice_input()
            if voice_text:
                st.write(f"Voice Input Recognized: {voice_text}")
                st.session_state.messages.append({"role": "user", "content": voice_text})
                with st.chat_message("user"):
                    st.markdown(voice_text)

                # Generate chatbot response
                assistant_response = chatbot_interaction(voice_text, st.session_state.get("username", "unknown_user"))
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

else:
    st.sidebar.info("Please select at least one subject from the sidebar to start.")
