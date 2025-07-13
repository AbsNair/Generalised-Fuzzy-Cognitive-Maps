import streamlit as st
from pathlib import Path

# --- App title & disclaimer ---
st.set_page_config(page_title="Welcome to GFCM Simulator", layout="wide")
st.title("🌐 Generalised Fuzzy Cognitive Maps Platform")

st.markdown("""
Welcome to the GFCM Explorer. This tool allows you to:
- Build and simulate Generalised Fuzzy Cognitive Maps (GFCMs)
- Upload matrices or draw interactively
- Export data for further simulation
""")

# --- Terms and Conditions ---
accept = st.checkbox("✅ I accept the Terms and Conditions")

with st.expander("Read Terms and Conditions"):
    st.markdown("""
    **Usage Notice:** This simulator is for educational and research purposes. Data entered into the platform is not stored or shared.

    By continuing, you agree that:
    - You are using this tool at your own risk.
    - You are responsible for the data you upload.
    - You acknowledge this is a public beta version.
    """)

if not accept:
    st.warning("Please accept the Terms and Conditions to proceed.")
    st.stop()

# --- Navigation ---
st.success("You may now choose a tool:")

tool = st.radio("Choose a module to open:", ["🧠 FCM Builder", "📊 GFCM Simulator"])

if tool == "🧠 FCM Builder":
    st.switch_page("cytoscape_fcm_editor_modal.py")
elif tool == "📊 GFCM Simulator":
    st.switch_page("app.py")
