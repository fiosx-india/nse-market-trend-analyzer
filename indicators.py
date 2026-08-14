import numpy as np
import pandas as pd

def calculate_technical_indicators(df):
    try:
        if df.empty or len(df) < 15:
            return df
            
        # 1. RSI (Relative Strength Index) - தூய்மையான கணித சூத்திரம்
        close = df['Close']
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        
        ema_gain = gain.ewm(com=13, adjust=False).mean()
        ema_loss = loss.ewm(com=13, adjust=False).mean()
        
        rs = ema_gain / (ema_loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. Moving Averages (EMA 9 & 21) - டிரெண்ட் காட்டி
        df['EMA_9'] = close.ewm(span=9, adjust=False).mean()
        df['EMA_21'] = close.ewm(span=21, adjust=False).mean()
        
        # 3. MACD & Signal Line - பிரேக்அவுட் இன்ஜின்
        df['MACD'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df
    except:
        return df
