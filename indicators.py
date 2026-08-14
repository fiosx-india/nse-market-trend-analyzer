import numpy as np
import pandas as pd
import pandas_ta as pta

def calculate_ultra_indicators(df):
    try:
        if df.empty or len(df) < 30:
            return None
            
        # ----------------- 1. மொமண்டம் மகா சக்திகள் (Momentum Indicators) -----------------
        # RSI (Relative Strength Index) & Stochastic Oscillator
        df.ta.rsi(length=14, append=True)
        df.ta.stoch(high='High', low='Low', close='Close', window=14, smooth_k=3, append=True)
        # CCI (Commodity Channel Index) & Williams %R
        df.ta.cci(length=20, append=True)
        df.ta.willr(length=14, append=True)
        
        # ----------------- 2. டிரெண்ட் & பிரேக்அவுட் அஸ்திரங்கள் (Trend Engines) -----------------
        # MACD (Moving Average Convergence Divergence)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        # ADX (Average Directional Index) - டிரெண்ட் வேகம் அறிய
        df.ta.adx(length=14, append=True)
        # Aroon Oscillator & SuperTrend
        df.ta.aroon(length=25, append=True)
        try:
            df.ta.supertrend(period=7, multiplier=3, append=True)
        except:
            pass
            
        # ----------------- 3. வால்யூம் & பல்க் டீல் டிராக்கர்கள் (Volume Smart Filters) -----------------
        # OBV (On-Balance Volume) & Chaikin Money Flow (CMF)
        df.ta.obv(append=True)
        df.ta.cmf(append=True)
        # MFI (Money Flow Index) - ஸ்மார்ட் பணம் உள்ளே வருகிறதா என அறிய
        df.ta.mfi(length=14, append=True)

        # ----------------- 4. அக்யூரசி வோட்டிங் சிஸ்டம் (AI Leadership Consensus) -----------------
        # அத்தனை இண்டிகேட்டர்களின் முடிவுகளையும் ஒரு தலைமை இன்ஜின் ஒருங்கிணைக்கிறது
        bullish_votes = 0
        bearish_votes = 0
        
        # காலம்களின் பெயர்களைத் தூய்மைப்படுத்துதல்
        df.columns = df.columns.str.upper()
        
        # லாஜிக் 1: RSI சரிபார்ப்பு
        if 'RSI_14' in df.columns:
            rsi = df['RSI_14'].iloc[-1]
            if 45 < rsi < 70: bullish_votes += 2
            elif rsi > 75 or rsi < 30: bearish_votes += 2
            
        # லாஜிக் 2: MACD பிரேக்அவுட்
        macd_cols = [c for col in df.columns if 'MACD_' in col]
        sig_cols = [c for col in df.columns if 'MACDS_' in col]
        if macd_cols and sig_cols:
            if df[macd_cols].iloc[-1] > df[sig_cols].iloc[-1]: bullish_votes += 2
            else: bearish_votes += 2
            
        # லாஜிக் 3: சூப்பர்டிரெண்ட் & மூவிங் ஆவரேஜ் கிராஸ்ஓவர்
        if 'CLOSE' in df.columns:
            df['EMA_9'] = df['CLOSE'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['CLOSE'].ewm(span=21, adjust=False).mean()
            if df['EMA_9'].iloc[-1] > df['EMA_21'].iloc[-1]: bullish_votes += 1.5
            else: bearish_votes += 1.5
            
        # லாஜிக் 4: MFI வால்யூம் பலம்
        if 'MFI_14' in df.columns:
            mfi = df['MFI_14'].iloc[-1]
            if mfi > 50: bullish_votes += 1
            else: bearish_votes += 1

        # ----------------- 5. 1, 2, 3 மணிநேர அக்யூரேட் கணிப்பு ரிப்போர்ட் -----------------
        current_price = df['CLOSE'].iloc[-1]
        
        if bullish_votes > bearish_votes + 1:
            prediction = "🚀 திங்கள் அன்று எகிறும் (Strong Bullish)"
            target_1h = current_price * 1.005
            target_3h = current_price * 1.015
        elif bearish_votes > bullish_votes + 1:
            prediction = "📉 வீழ்ச்சி அடையும் (Strong Bearish)"
            target_1h = current_price * 0.995
            target_3h = current_price * 0.985
        else:
            prediction = "💤 பெரிய மாற்றமிருக்காது (Flat Market)"
            target_1h = current_price
            target_3h = current_price

        return {
            "AI ஒட்டுமொத்த கணிப்பு": prediction,
            "1 மணிநேர டார்கெட் விலை (₹)": round(target_1h, 2),
            "3 மணிநேர டார்கெட் விலை (₹)": round(target_3h, 2),
            "இண்டிகேட்டர் பலம் (Score)": f"{bullish_votes} vs {bearish_votes}"
        }
    except Exception as e:
        return {
            "AI ஒட்டுமொத்த கணிப்பு": "டேட்டா பற்றாக்குறை ⚠️",
            "1 மணிநேர டார்கெட் விலை (₹)": 0.0,
            "3 மணிநேர டார்கெட் விலை (₹)": 0.0,
            "இண்டிகேட்டர் பலம் (Score)": "0 vs 0"
        }
