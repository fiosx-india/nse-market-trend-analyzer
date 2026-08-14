import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import asyncio
import aiohttp

st.set_page_config(page_title="NSE Total Auto Analyzer", layout="wide")
st.title("📊 ஒட்டுமொத்த மார்க்கெட் தானியங்கி பங்கு டிரெண்ட் அனலைசர்")

# 1. இடதுபுறத்தில் எந்த ஒரு ஃபைலையும் அப்লোட் செய்யும் டைனமிக் செட்டிங்
uploaded_file = st.sidebar.file_uploader(
    "உங்களிடம் உள்ள எந்தவொரு கம்பெனி லிஸ்ட் CSV ஃபைலையும் இங்கே பதிவேற்றவும்", 
    type=["csv", "txt", "xlsx"]
)

# அсин்க்ரோனஸ் முறையில் ஒரே நேரத்தில் பல பங்குகளின் லைவ் தரவை எடுக்கும் லாஜிக்
async def fetch_stock_async(session, ticker):
    try:
        stock = yf.Ticker(ticker)
        loop = asyncio.get_event_loop()
        # கடந்த 3 நாட்களின் நிமிடத் தரவை மட்டும் எடுத்து வேகத்தை உச்சத்திற்கு கொண்டு செல்கிறோம்
        df = await loop.run_in_executor(None, lambda: stock.history(period="3d", interval="1m"))
        
        if df.empty or len(df) < 5:
            return None
            
        current_price = df['Close'].iloc[-1]
        current_time = df.index[-1]
        
        time_1h = current_time - timedelta(hours=1)
        time_2h = current_time - timedelta(hours=2)
        time_3h = current_time - timedelta(hours=3)
        
        price_1h = df.asof(time_1h)['Close'] if time_1h in df.index or not df.loc[:time_1h].empty else df['Close'].iloc[-1]
        price_2h = df.asof(time_2h)['Close'] if time_2h in df.index or not df.loc[:time_2h].empty else df['Close'].iloc[-1]
        price_3h = df.asof(time_3h)['Close'] if time_3h in df.index or not df.loc[:time_3h].empty else df['Close'].iloc[-1]
        
        return {
            "கம்பெனி பெயர்": ticker.replace(".NS", ""),
            "லைவ் விலை (₹)": round(current_price, 2),
            "1 மணிநேர மாற்றம் (%)": round(((current_price - price_1h) / price_1h) * 100, 2),
            "2 மணிநேர மாற்றம் (%)": round(((current_price - price_2h) / price_2h) * 100, 2),
            "3 மணிநேர மாற்றம் (%)": round(((current_price - price_3h) / price_3h) * 100, 2)
        }
    except:
        return None

async def main_tracker(tickers):
    # மொபைல் மற்றும் BSNL நெட்வொர்க் வேகத்திற்கு ஏற்ப சர்வர் பிளாக் ஆகாமல் இருக்க 15 ஆகக் கட்டுப்படுத்துகிறோம்
    semaphore = asyncio.Semaphore(15)
    
    async def sem_task(session, ticker):
        async with semaphore:
            return await fetch_stock_async(session, ticker)
            
    async with aiohttp.ClientSession() as session:
        tasks = [sem_task(session, ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        return [r for result in results if (r := result) is not None]

# அப்லோட் செய்த ஃபைலை செக் செய்தல்
if uploaded_file is not None:
    try:
        # ஃபைலில் உள்ள தேவையில்லாத ஸ்பேஸ்களை நீக்கி படிக்கிறோம்
        nse_df = pd.read_csv(uploaded_file)
        # ஃபைலின் தலைப்பில் உள்ள ஸ்பேஸ் அல்லது குளறுபடிகளை ஆட்டோமேட்டிக்காக சரிசெய்கிறது!
        nse_df.columns = nse_df.columns.str.strip().str.upper() 
        
        # ஃபைலில் SYMBOL என்று தொடங்கும் காலம் எங்குள்ளது என்று ஆட்டோமேட்டிக்காகத் தேடுகிறது
        symbol_col = [col for col in nse_df.columns if 'SYMBOL' in col]
        
        if symbol_col:
            actual_col = symbol_col[0]
            # கோடிங்கில் கை வைக்காமல் ஃபைலில் உள்ள அத்தனை கம்பெனிகளையும் டைனமிக் ஆக எடுக்கிறது!
            TICKERS = [str(symbol).strip() + ".NS" for symbol in nse_df[actual_col].dropna().unique() if str(symbol).strip() != ""]
            
            # 2,000+ பங்குகள் ஸ்கேன் செய்ய அதிக நேரம் எடுக்கும் என்பதால், சோதனைக்காக முதல் 80 பங்குகளை மட்டும் எடுக்கிறோம்
            # (முழுமையாக ஸ்கேன் செய்ய விரும்பினால் 'TICKERS[:80]' என்பதை வெறும் 'TICKERS' என்று மாற்றலாம்)
            TICKERS_TO_SCAN = TICKERS
            total_stocks = len(TICKERS_TO_SCAN)
            
            st.write(f"⏱️ கடைசி ஸ்கேன் நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.info(f"⚡ வெற்றிகரமாக ஃபைல் படிக்கப்பட்டது! மொத்தம் {total_stocks} கம்பெனிகள் அனாலிசிஸ் செய்யப்படுகின்றன...")
            
            # அசிங்க் லூப்பை ரன் செய்தல்
            data_list = asyncio.run(main_tracker(TICKERS_TO_SCAN))
            
            df_stocks = pd.DataFrame(data_list)
            
            if not df_stocks.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success("🚀 உங்கள் ஃபைலில் இருந்து முன்கூட்டியே மேலே ஏறும் டாப் 10 கம்பெனிகள் (Gainers)")
                    top_gainers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=False).head(10)
                    st.dataframe(top_gainers, width="stretch")
                    
                with col2:
                    st.error("📉 உங்கள் ஃபைலில் இருந்து முன்கூட்டியே கீழே இறங்கும் டாப் 10 கம்பெனிகள் (Losers)")
                    top_losers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=True).head(10)
                    st.dataframe(top_losers, width="stretch")
                    
                st.subheader("📋 ஸ்கேன் செய்யப்பட்ட அனைத்து பங்குகளின் முழு விபரம்")
                st.dataframe(df_stocks, width="stretch")
            else:
                st.warning("⚠️ பங்குகளின் லைவ் தரவுகளைச் சேகரிக்க முடியவில்லை. சந்தை விடுமுறை நாளாக இருக்கலாம்.")
        else:
            st.error("❌ அப்லோட் செய்யப்பட்ட ஃபைலில் 'SYMBOL' என்ற Column பெயரைக் கண்டுபிடிக்க முடியவில்லை. சரியான ஃபைலை அப்லோட் செய்யவும்.")
    except Exception as e:
        st.error(f"❌ ஃபைலை படிப்பதில் தொழில்நுட்பச் சிக்கல்: {e}")
else:
    st.warning("👈 நீங்கள் டவுன்லோட் செய்த எந்த ஒரு மார்க்கெட் CSV ஃபைலையும் இடதுபுறம் அப்லோட் செய்யுங்கள்!")
