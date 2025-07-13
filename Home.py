import streamlit as st
from pathlib import Path

# --- App title & disclaimer ---------------------------------------------------
st.set_page_config(page_title="GFCM Launcher", layout="wide")
st.title("🌐 Generalised Fuzzy Cognitive Maps Platform")

st.markdown("""
Welcome to the **GFCM Explorer**. This tool allows you to:

- 🧠 **Build** interactive fuzzy cognitive maps using a visual editor  
- 💾 **Export** I and W matrices for use in simulations  
- 📊 **Simulate** GFCMs from uploaded matrices
""")

# --- Terms and Conditions -----------------------------------------------------
accept = st.checkbox("✅ I accept the Terms and Conditions")

with st.expander("Read Terms and Conditions"):
    st.markdown("""
**Usage Notice:** This simulator is for educational and research purposes.  
Data entered into the platform is not stored or shared.

By continuing, you agree that:
- You are using this tool at your own risk.  
- You are responsible for the data you upload.  
- You acknowledge this is a public beta version.  
    """)

if not accept:
    st.warning("Please accept the Terms and Conditions to proceed.")
    st.stop()

# --- Navigation ---------------------------------------------------------------
st.success("You may now choose a tool:")

tool = st.radio(
    "Choose a module to open:",
    ["🧠 FCM Builder", "📊 GFCM Simulator"]
)

if tool == "🧠 FCM Builder":
    # file lives at   pages/cytoscape_fcm_editor_modal.py
    st.switch_page("pages/cytoscape_fcm_editor_modal.py")
elif tool == "📊 GFCM Simulator":
    # file lives at   pages/app.py
    st.switch_page("pages/app.py")
