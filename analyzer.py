import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st

# 1. கண்காணிக்க வேண்டிய முன்னணி NSE கம்பெனிகளின் பட்டியல் (இதை நீங்கள் மாற்றிக் கொள்ளலாம்)
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS",
    "LT.NS", "MARUTI.NS", "HCLTECH.NS", "AXISBANK.NS", "SUNPHARMA.NS",
    "NTPC.NS", "TATAMOTORS.NS", "TITAN.NS", "COALINDIA.NS", "JIOFIN.NS"
]

def fetch_stock_data(tickers):
    data_list = []
    st.info("📊 இந்திய பங்குச்சந்தை (NSE) லைவ் தரவுகள் சேகரிக்கப்படுகின்றன, சற்று காத்திருக்கவும்...")
    
    for ticker in tickers:
        try:
            # 1 நிமிட இடைவெளியில் கடந்த 4 நாட்களின் தரவுகளை எடுத்தல்
            stock = yf.Ticker(ticker)
            df = stock.history(period="4d", interval="1m")
            
            if df.empty:
                continue
                
            current_price = df['Close'].iloc[-1]
            current_time = df.index[-1]
            
            # 1, 2, 3 மணிநேரத்திற்கு முந்தைய நேரங்களைக் கணக்கிடுதல்
            time_1h = current_time - timedelta(hours=1)
            time_2h = current_time - timedelta(hours=2)
            time_3h = current_time - timedelta(hours=3)
            
            # அந்தந்த நேரத்திற்கு மிக நெருக்கமான விலையை எடுத்தல்
            price_1h = df.asof(time_1h)['Close'] if time_1h in df.index or not df.loc[:time_1h].empty else df['Close'].iloc[0]
            price_2h = df.asof(time_2h)['Close'] if time_2h in df.index or not df.loc[:time_2h].empty else df['Close'].iloc[0]
            price_3h = df.asof(time_3h)['Close'] if time_3h in df.index or not df.loc[:time_3h].empty else df['Close'].iloc[0]
            
            # சதவீத மாற்றங்கள் (Percentage Change Logic)
            chg_1h = ((current_price - price_1h) / price_1h) * 100
            chg_2h = ((current_price - price_2h) / price_2h) * 100
            chg_3h = ((current_price - price_3h) / price_3h) * 100
            
            data_list.append({
                "கம்பெனி பெயர்": ticker.replace(".NS", ""),
                "லைவ் விலை (₹)": round(current_price, 2),
                "1 மணிநேர மாற்றம் (%)": round(chg_1h, 2),
                "2 மணிநேர மாற்றம் (%)": round(chg_2h, 2),
                "3 மணிநேர மாற்றம் (%)": round(chg_3h, 2)
            })
        except Exception as e:
            continue
            
    return pd.DataFrame(data_list)

# Streamlit பக்க வடிவமைப்பு (Web App UI)
st.set_page_config(page_title="NSE hourly Trend Tracker", layout="wide")
st.title("📊 NSE லைவ் மணிநேர பங்கு டிரெண்ட் அனலைசர்")
st.write(f"⏱️ கடைசியாகப் புதுப்பிக்கப்பட்ட நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

df_stocks = fetch_stock_data(TICKERS)

if not df_stocks.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🚀 நீங்கள் கேட்டபடி முன்கூட்டியே மேலே ஏறும் டாப் 10 கம்பெனிகள் (Gainers)")
        # 1 மணிநேரம் மற்றும் 2 மணிநேர ஏறுமுகத்தின் அடிப்படையில் ஃபில்டர் செய்தல்
        top_gainers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=False).head(10)
        st.dataframe(top_gainers, use_container_width=True)
        
    with col2:
        st.error("📉 நீங்கள் கேட்டபடி முன்கூட்டியே கீழே இறங்கும் டாப் 10 கம்பெனிகள் (Losers)")
        # சரிவின் அடிப்படையில் பில்டர் செய்தல்
        top_losers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=True).head(10)
        st.dataframe(top_losers, use_container_width=True)
        
    # அனைத்து கம்பெனிகளின் முழு பட்டியல்
    st.subheader("📋 கண்காணிப்பில் உள்ள அனைத்து கம்பெனிகளின் பட்டியல்")
    st.dataframe(df_stocks, use_container_width=True)
else:
    st.warning("⚠️ சந்தை தரவுகளை எடுக்க முடியவில்லை. பங்குச்சந்தை விடுமுறை நாளாக இருக்கலாம்.")
