import streamlit as st
import pandas as pd

st.set_page_config(page_title="NSE Market Analyzer", layout="wide")

st.title("📈 NSE Market Trend Analyzer")
st.write("NSE CSV ஃபைலை அப்லோட் செய்து, மார்க்கெட் ட்ரெண்டுகளை பகுப்பாய்வு செய்யவும்.")

# CSV அப்லோட் செய்யும் பகுதி
uploaded_file = st.file_uploader("NSE CSV ஃபைலை அப்லோட் செய்யவும்:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("ஃபைல் வெற்றிகரமாக அப்லோட் செய்யப்பட்டது!")
    
    # தரவு பகுப்பாய்வு (உதாரணத்திற்கு 'Symbol' மற்றும் 'Close' காலம்கள் இருப்பதாகக் கொள்கிறோம்)
    if 'Symbol' in df.columns and 'Close' in df.columns:
        # டாப் 10 மேலேறும் மற்றும் கீழே இறங்கும் பங்குகள் (Logic)
        top_gainers = df.nlargest(10, 'Close')
        top_losers = df.nsmallest(10, 'Close')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Top 10 Bullish Stocks")
            st.write(top_gainers[['Symbol', 'Close']])
            
        with col2:
            st.subheader("📉 Top 10 Bearish Stocks")
            st.write(top_losers[['Symbol', 'Close']])
            
        st.info("குறிப்பு: 1, 2, 3 மணி நேர இலக்குகள் மற்றும் சரிபார்ப்பு அறிக்கைகள் உங்கள் CSV-ல் உள்ள நேர அடிப்படையிலான தரவுகளைப் பொறுத்து உருவாக்கப்படும்.")
    else:
        st.error("பிழை: CSV ஃபைலில் 'Symbol' மற்றும் 'Close' காலம்கள் இல்லை.")
