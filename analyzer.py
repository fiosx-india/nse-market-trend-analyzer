import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import asyncio
import aiohttp
from PIL import Image
import numpy as np
import easyocr

# மற்ற அனைத்து உளவு மற்றும் இண்டிகேட்டர் ஃபைல்களை உள்ளே இழுக்கிறோம்!
import error_handler
import commodity_master
import indicators
import volume_tracker
import ai_engine

st.set_page_config(page_title="Ultimate Multi-Market Engine", layout="wide")
st.title("🔱 ஒட்டுமொத்த மார்க்கெட் திvவ்யாஸ்திர அனலைசர்")

market_type = st.sidebar.selectbox("மார்க்கெட் பிரிவு", ["📊 பங்குச்சந்தை (Stocks)", "🛢 கமாடிட்டி (Commodity)"])

def extract_symbols_from_image(uploaded_image):
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        image = Image.open(uploaded_image)
        img_np = np.array(image)
        with st.spinner("🔍 15 MP இமேஜ் சிப் ஸ்கேன் செய்யப்படுகிறது... கம்பெனி பெயர்கள் திரட்டப்படுகின்றன..."):
            result = reader.readtext(img_np, detail=0)
        detected_symbols = [str(w).strip().upper().replace(",", "").replace(" ", "") for w in result]
        return list(set([s for s in detected_symbols if s.isalnum() and 3 <= len(s) <= 12]))
    except:
        return []

async def fetch_stock_async(session, ticker, original_symbol=""):
    try:
        stock = yf.Ticker(ticker)
        loop = asyncio.get_event_loop()
        
        # 5 நொடி டைம்-அவுட் பாதுகாப்பு பூட்டு
        df = await error_handler.handle_with_timeout(
            loop.run_in_executor(None, lambda: stock.history(period="5d", interval="1m")), 
            timeout_seconds=5
        )
        
        if df is None or df.empty or len(df) < 15:
            return None
            
        current_price = df['Close'].iloc[-1]
        current_time = df.index[-1]
        
        price_1h = df.asof(current_time - timedelta(hours=1))['Close'] if not df.empty else current_price
        price_2h = df.asof(current_time - timedelta(hours=2))['Close'] if not df.empty else current_price
        price_3h = df.asof(current_time - timedelta(hours=3))['Close'] if not df.empty else current_price
        
        df = indicators.calculate_technical_indicators(df)
        bulk_status = volume_tracker.check_bulk_deals(df)
        ai_prediction = ai_engine.predict_next_hours_trend(df)
        
        return {
            "கம்பெனி பெயர்": original_symbol if original_symbol else ticker.replace(".NS", "").replace(".BO", ""),
            "நேரடி லைவ் விலை": round(current_price, 2),
            "1 மணிநேர மாற்றம் (%)": round(((current_price - price_1h) / price_1h) * 100, 2),
            "2 மணிநேர மாற்றம் (%)": round(((current_price - price_2h) / price_2h) * 100, 2),
            "3 மணிநேர மாற்றம் (%)": round(((current_price - price_3h) / price_3h) * 100, 2),
            "வால்யூம் அதிரடி (Bulk Alert)": bulk_status,
            "AI திங்கள் கணிப்பு (AE)": ai_prediction
        }
    except:
        return None

async def main_tracker(tickers_dict):
    semaphore = asyncio.Semaphore(15)
    async def sem_task(session, ticker, orig_sym):
        async with semaphore: return await fetch_stock_async(session, ticker, orig_sym)
    async with aiohttp.ClientSession() as session:
        tasks = [sem_task(session, ticker, orig_sym) for ticker, orig_sym in tickers_dict.items()]
        results = await asyncio.gather(*tasks)
        return [r for result in results if (r := result) is not None]

# ----------------- 📊 பிரிவு 1: பங்குச்சந்தை இன்ஜின் -----------------
if market_type == "📊 பங்குச்சந்தை (Stocks)":
    uploaded_file = st.sidebar.file_uploader("எந்தவொரு இமேஜ் ஸ்கிரீன்ஷாட் அல்லது CSV ஃபைலையும் இங்கே பதிவேற்றவும்", type=["csv", "txt", "xlsx", "png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        symbols = []
        
        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            symbols = extract_symbols_from_image(uploaded_file)
        else:
            try:
                df = pd.read_csv(uploaded_file)
                df.columns = df.columns.str.strip().str.upper()
                # 💥 திருத்தப்பட்ட பகுதி: லிஸ்ட்டில் இருந்து முதல் ஸ்ட்ரிங் தலைப்பை மட்டும் துல்லியமாக எடுக்கிறது!
                symbol_col = [col for col in df.columns if 'SYMBOL' in col or 'UNDERLYING' in col or 'CODE' in col]
                if symbol_col:
                    actual_col = symbol_col[0] # முதல் மேட்சிங் காலமை மட்டும் எடுக்கிறது
                    symbols = [str(sym).strip() for sym in df[actual_col].dropna().unique() if str(sym).strip() != ""]
            except:
                pass
                
        if symbols:
            TICKERS_DICT = {str(sym) + ".NS": str(sym) for sym in symbols[:100]}
            total_stocks = len(TICKERS_DICT)
            
            st.write(f"⏱️ கடைசி ஸ்கேன் நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.info(f"⚡ வெற்றிகரமாக ஃபைல் இணைக்கப்பட்டது! {total_stocks} கம்பெனிகள் 'சொரட்டி அடித்து' ஸ்கேன் செய்யப்படுகின்றன...")
            
            data_list = asyncio.run(main_tracker(TICKERS_DICT))
            df_stocks = pd.DataFrame(data_list)
            
            error_handler.display_safe_status(len(df_stocks), total_stocks)
            
            if not df_stocks.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.success("🚀 AI கணிப்பு படி முன்கூட்டியே மேலே ஏறும் டாப் 10 பங்குகள்")
                    top_gainers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=False).head(10)
                    st.dataframe(top_gainers, width="stretch")
                with col2:
                    st.error("📉 AI கணிப்பு படி முன்கூட்டியே கீழே இறங்கும் டாப் 10 பங்குகள்")
                    top_losers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=True).head(10)
                    st.dataframe(top_losers, width="stretch")
                st.subheader("📋 ஒட்டுமொத்த பங்குகளின் AI & பல்க் டீல் நேரடி ரிப்போர்ட்")
                st.dataframe(df_stocks, width="stretch")
        else:
            st.error("❌ ஃபைல் அல்லது இமேஜில் இருந்து கம்பெனி குறியீடுகளைப் பிரிக்க முடியவில்லை. தலைப்பில் 'SYMBOL' உள்ளதா என உறுதிப்படுத்தவும்.")

# ----------------- 🛢 பிரிவு 2: கமாடிட்டி இன்ஜின் -----------------
elif market_type == "🛢 கமாடிட்டி (Commodity)":
    st.write(f"⏱️ கடைசி ஸ்கேன் நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.info("🛢️ கமாடிட்டி மாஸ்டர் இன்ஜின் பின்னணியில் அத்தனை பங்குகளையும் ஸ்கேன் செய்கிறது...")
    
    COMM_DICT = commodity_master.get_all_commodities()
    total_comm = len(COMM_DICT)
    
    comm_data = asyncio.run(main_tracker(COMM_DICT))
    df_comm = pd.DataFrame(comm_data)
    
    error_handler.display_safe_status(len(df_comm), total_comm)
    
    if not df_comm.empty:
        st.success("📈 ஒட்டுமொத்த இந்திய (MCX) மற்றும் சர்வதேச கமாடிட்டி ரிப்போர்ட்")
        st.dataframe(df_comm, width="stretch")
