import streamlit as st
from db import init_db, login_user, register_user
from styles import load_css

# Init DB
init_db()

st.set_page_config(page_title="OcuVisionAI", layout="wide")

st.markdown(load_css(), unsafe_allow_html=True)
st.sidebar.markdown("## 🧭 Navigation")
st.sidebar.markdown("Use the pages below 👇")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.title("👁️ OcuVisionAI")

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:

    mode = st.sidebar.radio("Access", ["Login", "Signup"])

    if mode == "Login":
        st.title("🔐 Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user['id']
                st.session_state.user_name = user['name']
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.title("📝 Signup")

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            if register_user(name, email, password):
                st.success("Account created! Please login.")
            else:
                st.error("User already exists")

# ---------------- DASHBOARD ----------------
else:
    st.sidebar.success(f"Welcome {st.session_state.user_name}")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.title("👁️ OcuVisionAI Dashboard")

    st.markdown("""
    ### 🧠 AI-Powered Retinal Screening System

    - 📤 Upload retinal scans  
    - 📊 View history  
    - 📈 Track disease progression  
    """)

    st.info("Use the sidebar to navigate between modules")