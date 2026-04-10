from styles import load_css
import streamlit as st

st.markdown(load_css(), unsafe_allow_html=True)
from db import get_user_history

st.title("📊 History")

if 'user_id' not in st.session_state:
    st.stop()

data = get_user_history(st.session_state.user_id)

if not data:
    st.info("No records found")
else:
    for d in data:
        st.image(d['image_path'], width=200)
        st.write(d['prediction'], f"{d['confidence']*100:.2f}%")
        st.write(d['created_at'])
        st.markdown("---")