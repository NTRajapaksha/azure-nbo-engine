import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# --- CONFIGURATION ---
# PASTE YOUR AZURE URL HERE (Ensure it ends with /api/recommend)
API_URL = "https://nbo-api-lead-1126.azurewebsites.net/api/recommend"

# --- PAGE SETUP ---
st.set_page_config(page_title="NBO Engine | Lead Data Scientist Portfolio", layout="wide")

st.title("🏦 Next Best Offer (NBO) AI Engine")
st.markdown("""
*Real-Time Distributed Inference on Azure.*
Enter a Customer ID to retrieve the **Live AI Recommendation** from the cloud.
""")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Customer Lookup")
customer_id = st.sidebar.number_input("Customer ID", min_value=1, max_value=10000, value=15)
search_btn = st.sidebar.button("Generate Offer")

# --- MOCK CRM DATA GENERATOR ---
# Since we don't have the raw customer CSV loaded, we simulate 'CRM Data' 
# to give context to the AI decision.
def get_mock_customer_profile(cid):
    # Deterministic "random" data based on ID so it looks consistent
    fake_income = (cid * 1234) % 120000 + 30000
    fake_age = (cid * 56) % 60 + 18
    fake_segment = "High Net Worth" if fake_income > 80000 else "Mass Market"
    return {
        "Name": f"Customer-{cid}",
        "Age": fake_age,
        "Income": f"${fake_income:,.0f}",
        "Segment": fake_segment,
        "Risk Score": (cid * 7) % 100
    }

# --- MAIN LOGIC ---
if search_btn:
    # 1. Show Customer Profile (The "Context")
    profile = get_mock_customer_profile(customer_id)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customer", profile["Name"])
    col2.metric("Segment", profile["Segment"])
    col3.metric("Annual Income", profile["Income"])
    col4.metric("Risk Score", f"{profile['Risk Score']}/100")
    
    st.divider()

    # 2. Call Azure API (The "AI")
    st.subheader(f"📡 Real-Time AI Inference")
    
    with st.spinner(f"Calling Azure Function Endpoint for ID {customer_id}..."):
        try:
            start_time = time.time()
            
            # CALL THE API
            response = requests.get(f"{API_URL}?id={customer_id}")
            latency = (time.time() - start_time) * 1000 # ms
            
            if response.status_code == 200:
                offers = response.json()
                
                # METRICS
                st.success(f"Success! Latency: {latency:.0f}ms")
                
                # DISPLAY OFFERS
                st.markdown("### 🎯 Recommended Products")
                
                # Create 3 columns for the top 3 offers
                offer_cols = st.columns(3)
                
                for i, offer in enumerate(offers[:3]):
                    with offer_cols[i]:
                        # Card Styling
                        st.info(f"**Rank {i+1}**")
                        st.markdown(f"### {offer['name']}")
                        st.caption(offer['category'])
                        
                        # Score Bar
                        score = offer['prediction_score']
                        st.progress(min(score, 1.0))
                        st.write(f"Propensity Score: **{score:.4f}**")
                        
                        if st.button(f"Accept Offer {i+1}", key=f"btn_{i}"):
                            st.balloons()
                            st.toast(f"Offer '{offer['name']}' Accepted!")

                # RAW DATA EXPANDER (For the Technical Interviewer)
                with st.expander("View Raw JSON Response"):
                    st.json(offers)
                    
            elif response.status_code == 404:
                st.warning("No recommendations found for this user. (Cold Start User?)")
            else:
                st.error(f"API Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")

else:
    st.info("👈 Enter a Customer ID in the sidebar to begin.")