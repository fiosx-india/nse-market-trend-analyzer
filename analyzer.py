import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import asyncio
import aiohttp

st.set_page_config(page_title="NSE & MCX Rupee Analyzer", layout="wide")

# இடதுபுறத்தில் பக்கங்களை மாற்றுவதற்கான செட்டிங் (Navigation)
page = st.sidebar.selectbox("பக்கத்தைத் தேர்வு செய்யவும்", ["📊 பங்குச்சந்தை (Stocks)", "🛢 கமாடிட்டி (Commodity)"])

# அсин்க்ரோனஸ் முறையில் ஒரே நேரத்தில் லைவ் தரவை எடுக்கும் லாஜிக்
async def fetch_stock_async(session, ticker, is_commodity=False):
    try:
        stock = yf.Ticker(ticker)
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(None, lambda: stock.history(period="3d", interval="1m"))
        
        if df.empty or len(df) < 2:
            return None
            
        current_price = df['Close'].iloc[-1]
        current_time = df.index[-1]
        
        time_1h = current_time - timedelta(hours=1)
        time_2h = current_time - timedelta(hours=2)
        time_3h = current_time - timedelta(hours=3)
        
        price_1h = df.asof(time_1h)['Close'] if time_1h in df.index or not df.loc[:time_1h].empty else df['Close'].iloc[-1]
        price_2h = df.asof(time_2h)['Close'] if time_2h in df.index or not df.loc[:time_2h].empty else df['Close'].iloc[-1]
        price_3h = df.asof(time_3h)['Close'] if time_3h in df.index or not df.loc[:time_3h].empty else df['Close'].iloc[-1]
        
        name = ticker
        if is_commodity:
            name_dict = {
                "GC=F": "சர்வதேச தங்கம் (Gold - $)", 
                "24KGOLDM.NS": "MCX இந்திய தங்கம் (Gold 10g - ₹)",
                "SI=F": "சர்வதேச வெள்ளி (Silver - $)", 
                "SILVERM.NS": "MCX இந்திய வெள்ளி (Silver 1kg - ₹)",
                "CL=F": "சர்வதேச கச்சா எண்ணெய் (Crude - $)",
                "CRUDEOIL.NS": "MCX இந்திய கச்சா எண்ணெய் (Crude - ₹)"
            }
            name = name_dict.get(ticker, ticker)

        return {
            "பொருள்/கம்பெனி பெயர்": name,
            "லைவ் விலை மதிப்பு": round(current_price, 2),
            "1 மணிநேர மாற்றம் (%)": round(((current_price - price_1h) / price_1h) * 100, 2),
            "2 மணிநேர மாற்றம் (%)": round(((current_price - price_2h) / price_2h) * 100, 2),
            "3 மணிநேர மாற்றம் (%)": round(((current_price - price_3h) / price_3h) * 100, 2)
        }
    except:
        return None

async def main_tracker(tickers, is_commodity=False):
    semaphore = asyncio.Semaphore(15)
    async def sem_task(session, ticker):
        async with semaphore:
            return await fetch_stock_async(session, ticker, is_commodity)
    async with aiohttp.ClientSession() as session:
        tasks = [sem_task(session, ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        return [r for result in results if (r := result) is not None]

# ----------------- பக்கம் 1: பங்குச்சந்தை அனாலிசிஸ் (பழைய வசதி அப்படியே உள்ளது!) -----------------
if page == "📊 பங்குச்சந்தை (Stocks)":
    st.title("📊 ஒட்டுமொத்த மார்க்கெட் தானியங்கி பங்கு டிரெண்ட் அனலைசர்")
    uploaded_file = st.sidebar.file_uploader("உங்களிடம் உள்ள எந்தவொரு கம்பெனி லிஸ்ட் CSV ஃபைலையும் இங்கே பதிவேற்றவும்", type=["csv", "txt", "xlsx"])

    if uploaded_file is not None:
        try:
            nse_df = pd.read_csv(uploaded_file)
            nse_df.columns = nse_df.columns.str.strip().str.upper() 
            symbol_col = [col for col in nse_df.columns if 'SYMBOL' in col]
            
            if symbol_col:
                actual_col = symbol_col[0] # முதல் மேட்சிங் காலமை எடுக்கிறது
                TICKERS = [str(symbol).strip() + ".NS" for symbol in nse_df[actual_col].dropna().unique() if str(symbol).strip() != ""]
                
                TICKERS_TO_SCAN = TICKERS
                total_stocks = len(TICKERS_TO_SCAN)
                
                st.write(f"⏱️ கடைசி ஸ்கேன் நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.info(f"⚡ வெற்றிகரமாக ஃபைல் படிக்கப்பட்டது! மொத்தம் {total_stocks} கம்பெனிகள் அனாலிசிஸ் செய்யப்படுகின்றன. சற்று காத்திருக்கவும்...")
                
                data_list = asyncio.run(main_tracker(TICKERS_TO_SCAN, is_commodity=False))
                df_stocks = pd.DataFrame(data_list)
                
                if not df_stocks.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success("🚀 முன்கூட்டியே மேலே ஏறும் டாப் 10 கம்பெனிகள் (Gainers)")
                        top_gainers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=False).head(10)
                        st.dataframe(top_gainers, width="stretch")
                    with col2:
                        st.error("📉 முன்கூட்டியே கீழே இறங்கும் டாப் 10 கம்பெனிகள் (Losers)")
                        top_losers = df_stocks.sort_values(by=["1 மணிநேர மாற்றம் (%)", "2 மணிநேர மாற்றம் (%)"], ascending=True).head(10)
                        st.dataframe(top_losers, width="stretch")
                    
                    st.subheader("📋 ஸ்கேன் செய்யப்பட்ட அனைத்து பங்குகளின் முழு விபரம்")
                    st.dataframe(df_stocks, width="stretch")
                else:
                    st.warning("⚠️ பங்குகளின் லைவ் தரவுகளைச் சேகரிக்க முடியவில்லை.")
            else:
                st.error("❌ ஃபைலில் 'SYMBOL' என்ற Column பெயரைக் கண்டுபிடிக்க முடியவில்லை.")
        except Exception as e:
            st.error(f"❌ ஃபைலை படிப்பதில் தொழில்நுட்பச் சிக்கல்: {e}")
    else:
        st.warning("👈 நீங்கள் டவுன்லோட் செய்த எந்த ஒரு மார்க்கெட் CSV ஃபைலையும் இடதுபுறம் அப்லோட் செய்யுங்கள்!")

# ----------------- பக்கம் 2: கமாடிட்டி அனாலிசிஸ் (ரூபாய் மற்றும் டாலர் இரண்டுமே வரும்!) -----------------
elif page == "🛢 கமாடிட்டி (Commodity)":
    st.title("🛢 லைவ் கமாடிட்டி (டாலர் & இந்திய ரூபாய்) டிரெண்ட் அனலைசர்")
    st.write("தங்கம், வெள்ளி, கச்சா எண்ணெய் ஆகியவற்றின் நேரடி 1, 2, 3 மணிநேரக் கண்காணிப்பு (இரவு 11:30 மணி வரை லைவ் விலைகள் மாறும்).")
    st.write(f"⏱️ கடைசி ஸ்கேன் நேரம்: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # சர்வதேச மற்றும் இந்திய MCX ரூபாய் குறியீடுகள் ஒன்றாக இணைக்கப்பட்டுள்ளது
    COMMODITY_TICKERS = ["GC=F", "24KGOLDM.NS", "SI=F", "SILVERM.NS", "CL=F", "CRUDEOIL.NS"]
    
    with st.spinner("🔄 கமாடிட்டி மற்றும் இந்திய ரூபாய் (MCX) லைவ் விலைகள் சேகரிக்கப்படுகின்றன..."):
        comm_data = asyncio.run(main_tracker(COMMODITY_TICKERS, is_commodity=True))
        df_comm = pd.DataFrame(comm_data)
        
        if not df_comm.empty:
            st.success("📈 தற்போதைய உலகளாவிய மற்றும் இந்திய கமாடிட்டி சந்தை நிலவரம்")
            st.dataframe(df_comm, width="stretch")
            
            st.info("💡 குறிப்பு: டாலர் ($) குறியீடு உள்ளவை சர்வதேச சந்தை விலைகள். ரூபாய் (₹) குறியீடு உள்ளவை இந்திய MCX சந்தையின் நேரடி லைவ் விலைகள் ஆகும்.")
        else:
            st.warning("⚠️ கماடிட்டி லைவ் தரவுகளைச் சேகரிக்க முடியவில்லை. மார்க்கெட் விடுமுறையாக இருக்கலாம் அல்லது இணையச் சிக்கல்.")
