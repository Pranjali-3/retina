from styles import load_css
import streamlit as st

st.markdown(load_css(), unsafe_allow_html=True) 
import os
from utils.model_utils import predict
from db import save_prediction

st.title("📤 Upload & Diagnose")

if 'user_id' not in st.session_state:
    st.warning("Login required")
    st.stop()

file = st.file_uploader("Upload Fundus Image", type=["jpg", "png"])

if file:
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    path = os.path.join("uploads", file.name)

    with open(path, "wb") as f:
        f.write(file.getbuffer())

    st.image(path, width=400)

    if st.button("Analyze"):
        pred, conf = predict(path)

        save_prediction(st.session_state.user_id, path, pred, conf)

        st.success(f"Diagnosis: {pred}")
        st.write(f"Confidence: {conf*100:.2f}%")

        if pred != "No_DR":
            st.error("⚠️ Refer to specialist")