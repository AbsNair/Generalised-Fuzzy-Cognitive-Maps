import streamlit as st

st.set_page_config(page_title="GFCM Launcher", layout="wide")

# --- App Title & Introduction ---
st.title("🌐 Generalised Fuzzy Cognitive Maps Platform")

st.markdown("""
Welcome to the **GFCM Explorer**. This tool allows you to:

- 🧠 **Build** interactive fuzzy cognitive maps using a visual editor  
- 📊 **Simulate** GFCMs from uploaded matrices  
- 💾 **Export** I and W matrices for use in simulations
""")

# --- Terms and Conditions ---
accept = st.checkbox("✅ I accept the Terms and Conditions")

with st.expander("Read Terms and Conditions"):
    st.markdown("""
    **Usage Notice**  
    This simulator is intended for research and educational use only.  
    By continuing, you agree to:
    
    - Use this tool responsibly at your own discretion  
    - Avoid uploading sensitive data  
    - Accept that this is a prototype with no data persistence  
    """)

if not accept:
    st.warning("Please accept the Terms and Conditions to continue.")
    st.stop()

# --- Tool Selection ---
st.success("Terms accepted. You may now choose a tool.")

tool = st.radio("Choose a module to open:", ["🧠 FCM Builder", "📊 GFCM Simulator"])

if tool == "🧠 FCM Builder":
    st.switch_page("cytoscape_fcm_editor_modal")  # This must live inside pages/
elif tool == "📊 GFCM Simulator":
    st.switch_page("app")  # This must live inside pages/
