from styles import load_css
import streamlit as st

st.markdown(load_css(), unsafe_allow_html=True)
import pandas as pd
from db import get_user_history

st.title("📈 Progression Analysis")

SEVERITY = {
    "No_DR": 0,
    "Mild": 1,
    "Moderate": 2,
    "Severe": 3,
    "Proliferative_DR": 4
}

if 'user_id' not in st.session_state:
    st.stop()

data = get_user_history(st.session_state.user_id)

if not data:
    st.info("No data available")
else:
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at')
    df['severity'] = df['prediction'].map(SEVERITY)

    st.dataframe(df[['created_at', 'prediction', 'confidence']])
    st.line_chart(df.set_index('created_at')['severity'])

    if len(df) > 1:
        if df['severity'].iloc[-1] > df['severity'].iloc[0]:
            st.error("Condition worsening")
        else:
            st.success("Stable or improving")