import pandas as pd

def predict_next_hours_trend(df):
    try:
        if df.empty or 'RSI' not in df.columns:
            return "ஊகிக்க முடியாது"
            
        current_rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1] if 'MACD' in df.columns else 0
        signal = df['Signal_Line'].iloc[-1] if 'Signal_Line' in df.columns else 0
        
        # எளிய மொமண்டம் வோட்டிங் லாஜிக்
        score = 0
        if macd > signal: score += 1
        if 40 < current_rsi < 70: score += 1
        
        if score >= 1:
            return "🚀 திங்கள் அன்று மேலே ஏறும் (Strong Bullish)"
        else:
            return "📉 சரிவு / அசைவின்றி இருக்கும் (Neutral/Bearish)"
    except:
        return "டேட்டா பற்றாக்குறை"

