import os
import base64
import hashlib
import json
import sqlite3
import streamlit as st
import subprocess
import pandas as pd
import chat
import url
import pdf

# Add gradient background or image with overlay
def add_bg():
    st.markdown(
    f"""
    <style>
    /* Background styling */
    .stApp {{
        background: linear-gradient(to right, #d3cce3, #e9e4f0);
        font-family: 'Arial', sans-serif;
        color: #333;
    }}
    /* Hide navbar by default, display only if logged in */
    .navbar {{
       display: none;
    }}
    .stApp .navbar {{
        display: block;
        background-color: #333;
        overflow: hidden;
        position: fixed;
        top: 0;
        width: 100%;
        z-index: 9999;
        height: 60px;
        color: white;
        text-align: center;
    }}

    .navbar a {{
        float: left;
        color: white;
        text-decoration: none;
        padding: 15px 20px;
        font-size: 17px;
    }}

    .navbar a:hover {{
        background-color: #ddd;
        color: black;
    }}

    .navbar-brand {{
        font-size: 25px;
        font-weight: bold;
    }}
    /* Button styling */
    .button {{
        background-color: #6200ea;
        color: white;
        padding: 10px 24px;
        font-size: 16px;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease-in-out;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        margin-top: 10px;
    }}
    .button:hover {{
        background-color: #3700b3;
        color: #fff;
        transform: translateY(-3px);
    }}
    .navbar-brand {{
        float: left;
        padding: 14px 20px;
        font-size: 25px;
        font-weight: bold;
    }}
    /* Optional styling for inputs and buttons */
    .stTextInput > div > input {{
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        width: 100%;
    }}
    .stButton > button {{
        width: 100%;
        padding: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }}
    /* Login card styling */
    .login-card {{
        padding: 30px;
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 400px;
        text-align: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

add_bg()

# # Hash password using SHA256
# def hash_password(password):
#     return hashlib.sha256(str.encode(password)).hexdigest()
def encode_file_content(file_content):
    return base64.b64encode(file_content).decode("utf-8")

def decode_file_content(encoded_content):
    return base64.b64decode(encoded_content)
# Load existing users data
def load_users_db():
    try:
        with open("users_db.json", "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        st.warning("Corrupted database file. Starting with an empty database.")
        return {}  # Start fresh if JSON is invalid
    except FileNotFoundError:
        st.info("Database file not found. Creating a new one.")
        return {}  # Initialize a new database if file is missing

# Save users data to a file
def save_users_db():
    with open("users_db.json", "w") as file:
        json.dump(users_db, file, indent=4)  # Add indent for readability

# Load users data
users_db = load_users_db()

# Custom navbar for navigation
def custom_navbar():
    # if st.session_state.logged_in:
        st.markdown(
            """
            <div class="navbar">
              <a class="navbar-brand" href="#home">Edu-Assist</a>
              <a href="#profile">Profile</a>
              <div class="dropdown">
                <button class="dropbtn">Dashboard</button>
                <div class="dropdown-content">
                  <a href="#dashboard">User Dashboard</a>
                  <a href="#admin_dashboard">Admin Dashboard</a>
                </div>
              </div>
              <a href="#logout">Logout</a>
            </div>
            """, unsafe_allow_html=True)

# Sign-up new user
# def signup(username, password, email):
#     if username not in users_db:
#         users_db[username] = {
#             "password": hash_password(password),
#             "email": email,
#             "contact": "",
#             "profile_pic": "",
#             "uploaded_files": [],
#             "activity_count": {
#                 "chat_sessions": 0,
#                 "pdf_processed": 0,
#                 "urls_explored": 0
#             }
#         }
#         save_users_db()
#         return True
#     return False

# # Login and Sign-Up functionality
# def login_signup():
#     st.markdown('<div class="login-card">', unsafe_allow_html=True)

#     st.title("Login / Sign Up")
#     option = st.radio("Choose", ["Login", "Sign Up"])

#     if option == "Login":
#         st.subheader("Login")
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
        
#         if st.button("Login"):
#             if username in users_db and users_db[username]["password"] == hash_password(password):
#                 st.session_state.logged_in = True
#                 st.session_state.username = username
#                 st.success(f"Welcome {username}!")
#             else:
#                 st.error("Invalid username or password.")
    
#     elif option == "Sign Up":
#         st.subheader("Sign Up")
#         username = st.text_input("New Username")
#         email = st.text_input("Email")
#         password = st.text_input("New Password", type="password")
#         confirm_password = st.text_input("Confirm Password", type="password")

#         if password != confirm_password:
#             st.warning("Passwords do not match.")
#         elif st.button("Sign Up"):
#             if signup(username, password, email):
#                 st.success("Sign up successful! You can now log in.")
#             else:
#                 st.error("Username already exists.")

#     st.markdown('</div>', unsafe_allow_html=True)  # Close login-card

# def user_profile(username):
#     st.title(f"Welcome, {username}!")
#     st.subheader("User Profile")
#     tabs = st.tabs(["Profile", "Uploaded Files", "Stats"])

#     if username not in users_db:
#         st.error("User not found.")
#         return

#     user_data = users_db[username]
#     if "uploaded_files" not in user_data:
#         user_data["uploaded_files"] = []

#     # Profile Tab
#     with tabs[0]:
#         st.write("Profile Details")
#         email = user_data.get('email', "Email not set")
#         contact = user_data.get('contact', "Contact not set")

#         email_input = st.text_input("Email", value=email)
#         contact_input = st.text_input("Contact", value=contact)

#         if st.button("Save Changes"):
#             if email_input != email or contact_input != contact:
#                 user_data['email'] = email_input
#                 user_data['contact'] = contact_input
#                 users_db[username] = user_data
#                 save_users_db()
#                 st.success("Profile updated successfully!")
#             else:
#                 st.info("No changes detected.")

#     # Uploaded Files Tab
#     with tabs[1]:
#         st.write("Uploaded Files")

#         uploaded_file = st.file_uploader("Upload a file")
        
#         if uploaded_file:
#             file_data = {
#                 "name": uploaded_file.name,
#                 "type": uploaded_file.type,
#                 "content": encode_file_content(uploaded_file.read())  # Encode to base64
#             }
            
#             user_data["uploaded_files"].append(file_data)
#             users_db[username] = user_data
#             save_users_db()

#             st.success("File uploaded successfully!")

#         if user_data["uploaded_files"]:
#             for i, file in enumerate(user_data["uploaded_files"], 1):
#                 st.write(f"File {i}: {file['name']} ({file['type']}) - Preview: {file['content'][:50]}...")

#     # Stats Tab
#     with tabs[2]:
#         st.write("User Stats")
#         activity_count = user_data.get("activity_count", 0)
#         st.write(f"Activity Count: {activity_count}")

#         stats = user_data.get("stats", {})
#         for stat, value in stats.items():
#             st.write(f"{stat.capitalize()}: {value}")


# def add_new_user(username):
#     if username not in users_db:
#         users_db[username] = {'activity_count': 0}
# def record_activity(username):
#     if username in users_db:
#         users_db[username]['activity_count'] += 1  # Increment activity count
#         st.write(f"Recorded activity for {username}. New activity_count: {users_db[username]['activity_count']}")
#     else:
#         # If user doesn't exist, create them with initial activity count
#         users_db[username] = {'activity_count': 1}
#         st.write(f"User '{username}' not found in database. Added with activity_count set to 1.")

# Dashboard with Plotly visualizations
# def student_dashboard(username):
#     st.title(f"Dashboard for {username}")
#     if username in users_db:
#         activity_counts = users_db[username].get('activity_count', 0)
#         st.write(f"Activity Count for {username}: {activity_counts}")
#     else:
#         st.error(f"User '{username}' not found in the database.")
#     activity_counts = users_db[username]['activity_count']
#     data = {
#         'Activity': ['Chat Sessions', 'PDFs Processed', 'URLs Explored'],
#         'Count': [activity_counts['chat_sessions'], activity_counts['pdf_processed'], activity_counts['urls_explored']]
#     }
#     df = pd.DataFrame(data)
#     fig = px.bar(df, x='Activity', y='Count', color='Activity',
#                  title="User Activity Summary",
#                  labels={'Count':'Activity Count'}, height=400)
#     st.plotly_chart(fig)

# Main tool interface
def main_tool_interface():
    st.markdown('<p style="text-align: center; font-size: 2.5em;">AI Study Tool 🚀</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card"><p class="chat">🤖 CHATIFY</p>', unsafe_allow_html=True)
        if st.button("Chat Bot", help="Chat with our AI Chatbot", use_container_width=True):
            subprocess.run(["streamlit", "run", "chat.py"])
            # users_db[st.session_state.username]["activity_count"]["chat_sessions"] += 1
            save_users_db()
            st.success("Chat session recorded!")
        st.markdown('<p class="c1">Chat with AI Bot to ask questions.</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><p class="chat">🕸️ WEBIFY</p>', unsafe_allow_html=True)
        if st.button("URL Explorer", help="Explore URLs", use_container_width=True):
            subprocess.run(["streamlit", "run", "URL.py"])
            # users_db[st.session_state.username]["activity_count"]["urls_explored"] += 1
            save_users_db()
            st.success("URL exploration recorded!")
        st.markdown('<p class="c1">Explore and analyze URLs.</p>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><p class="chat">📄 DOCIFY</p>', unsafe_allow_html=True)
        if st.button("PDF Uploader", help="Upload PDFs", use_container_width=True):
            subprocess.run(["streamlit", "run", "pdf.py"])
            # users_db[st.session_state.username]["activity_count"]["pdf_processed"] += 1
            save_users_db()
            st.success("PDF processed recorded!")
        st.markdown('<p class="c1">Upload and process PDF files.</p>', unsafe_allow_html=True)

# Main app logic
def main():
    # if "logged_in" not in st.session_state:
    #     st.session_state.logged_in = False

    # # if not st.session_state.logged_in:
    # #     login_signup()
    # else:
        custom_navbar()
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Select a page", ["Home", "Profile", "Dashboard", "Log Out"])
        
        if page == "Home":
            main_tool_interface()
        # elif page == "Profile":
        #     # user_profile(st.session_state.username)
        # elif page == "Dashboard":
        #     username = st.session_state.username
            # add_new_user(username)
            # student_dashboard(username)
        # elif page == "Log Out":
        #     st.session_state.logged_in = False
        #     st.success("You have logged out.")

if __name__ == "__main__":
    main()
