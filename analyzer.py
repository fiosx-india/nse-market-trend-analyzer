import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st

# 1. கண்காணிக்க வேண்டிய முன்னணி NSE கம்பெனிகளின் பட்டியல்
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LTIM.NS",
    "BAJFINANCE.NS", "LT.NS", "MARUTI.NS", "HCLTECH.NS", "AXISBANK.NS",
    "SUNPHARMA.NS", "NTPC.NS", "TATAMOTORS.NS", "TITAN.NS", "COALINDIA.NS"
]

def fetch_stock_data(tickers):
    data_list = []
    st.info("சந்தைத் தரவுகள் சேகரிக்கப்படுகின்றன, சற்று காத்திருக்கவும்...")
    
    for ticker in tickers:
        try:
            # 1 நிமிட இடைவெளியில் கடந்த 4 நாட்களின் தரவுகளை எடுத்தல்
            stock = yf.Ticker(ticker)
            df = stock.history(period="4d", interval="1m")
            
            if df.empty:
                continue
                
            current_price = df['Close'].iloc[-1]
            current_time = df.index[-1]
            
            # 1, 2, 3 மணிநேரத்திற்கு முந்தைய விலைகளைக் கணக்கிடுதல்
            time_1h = current_time - timedelta(hours=1)
            time_2h = current_time - timedelta(hours=2)
            time_3h = current_time - timedelta(hours=3)
            
            # அதற்கு நெருக்கமான நேரத்தின் விலையை எடுத்தல்
            price_1h = df.asof(time_1h)['Close'] if time_1h in df.index or not df.loc[:time_1h].empty else df['Close'].iloc[0]
            price_2h = df.asof(time_2h)['Close'] if time_2h in df.index or not df.loc[:time_2h].empty else df['Close'].iloc[0]
            price_3h = df.asof(time_3h)['Close'] if time_3h in df.index or not df.loc[:time_3h].empty else df['Close'].iloc[0]
            
            # சதவீத மாற்றங்கள் (Percentage Change)
            chg_1h = ((current_price - price_1h) / price_1h) * 100
            chg_2h = ((current_price - price_2h) / price_2h) * 100
            chg_3h = ((current_price - price_3h) / price_3h) * 100
            
            data_list.append({
                "Company": ticker.replace(".NS", ""),
                "Current Price (₹)": round(current_price, 2),
                "1 Hour Change (%)": round(chg_1h, 2),
                "2 Hour Change (%)": round(chg_2h, 2),
                "3 Hour Change (%)": round(chg_3h, 2)
            })
        except Exception as e:
            continue
            
    return pd.DataFrame(data_list)

# Streamlit ஆப் வடிவமைப்பு
st.set_page_config(page_title="NSE Live Hourly Tracker", layout="wide")
st.title("📊 NSE லைவ் மணிநேர பங்கு கண்காணிப்பாளர்")
st.write(f"கடைசியாகப் புதுப்பிக்கப்பட்ட நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

df_stocks = fetch_stock_data(TICKERS)

if not df_stocks.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🚀 அடுத்த சில மணிநேரங்களில் மேலே ஏற வாய்ப்புள்ள டாப் 10 பங்குகள்")
        # 1, 2, 3 மணிநேர ஏறுமுகத்தின் அடிப்படையில் வரிசைப்படுத்துதல்
        top_gainers = df_stocks.sort_values(by=["1 Hour Change (%)", "2 Hour Change (%)"], ascending=False).head(10)
        st.dataframe(top_gainers, use_container_width=True)
        
    with col2:
        st.error("📉 அடுத்த சில மணிநேரங்களில் கீழே இறங்க வாய்ப்புள்ள டாப் 10 பங்குகள்")
        # சரிவின் அடிப்படையில் வரிசைப்படுத்துதல்
        top_losers = df_stocks.sort_values(by=["1 Hour Change (%)", "2 Hour Change (%)"], ascending=True).head(10)
        st.dataframe(top_losers, use_container_width=True)
        
    # முழு பட்டியல்
    st.subheader("📋 அனைத்து பங்குகளின் நேரடி நிலை")
    st.dataframe(df_stocks, use_container_width=True)
else:
    st.warning("தரவுகளைச் சேகரிப்பதில் சிக்கல் உள்ளது. சந்தை லீவு நாளாக இருக்கலாம்.")
