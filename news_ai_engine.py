import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta

def analyze_company_news_and_trend(ticker_symbol):
    try:
        # 1. நொடிப் பொழுதில் லைவ் செய்திகளைத் திரட்டுதல் (News Aggregator)
        clean_ticker = ticker_symbol.replace(".NS", "").replace(".BO", "")
        # இலவச கூகுள் நியூஸ் ஆர்.எஸ்.எஸ் (RSS) ஃபீட் மூலம் செய்திகளை எடுத்தல்
        news_url = f"https://google.com{clean_ticker}+stock+news&hl=en-IN&gl=IN&ceid=IN:en"
        
        # குறிப்பு: கார்ப்பரேட் அறிவிப்புகள் மற்றும் பல்க் டீல் செய்திகளை அறிய இந்த சென்டிமென்ட் உதவுகிறது
        sentiment_score = 0.0
        news_count = 0
        
        try:
            response = requests.get(news_url, timeout=5)
            # செய்திகளின் தலைப்பில் உள்ள முக்கிய வார்த்தைகளை ஸ்கேன் செய்தல்
            titles = [line.split('<title>')[1].split('</title>')[0] for line in response.text.split('\n') if '<title>' in line]
            
            for title in titles[:5]:  # டாப் 5 முக்கிய செய்திகளை மட்டும் ஆராய்தல்
                news_count += 1
                title_upper = title.upper()
                # பாசிட்டிவ் மற்றும் நெகட்டிவ் வார்த்தைகள் ஸ்கேனிங்
                if any(x in title_upper for x in ['PROFIT', 'ORDER', 'BUY', 'GROWTH', 'BULLISH', 'ACQUISITION', 'BONUS']):
                    sentiment_score += 1.5
                if any(x in title_upper for x in ['LOSS', 'FALL', 'SELL', 'BEARISH', 'FRAUD', 'DROP', 'REJECT']):
                    sentiment_score -= 1.5
        except:
            pass

        # 2. தற்போதைய சந்தை விலை மற்றும் வால்யூம் தரவுகளை எடுத்தல்
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="5d", interval="1m")
        
        if df.empty or len(df) < 10:
            return {"சிக்னல்": "டேட்டா பற்றாக்குறை", "டார்கெட்": 0.0}
            
        current_price = df['Close'].iloc[-1]
        
        # 3. செய்தி சென்டிமென்ட் மற்றும் விலை நகர்வை ஒருங்கிணைக்கும் AI லாஜிக்
        if sentiment_score > 1.0:
            prediction = "🚀 பலமான செய்தி ஆதரவு (Bullish Extension)"
            estimated_target = current_price * 1.012  # +1.2% சாத்தியமான உயர்வு இலக்கு
        elif sentiment_score < -1.0:
            prediction = "📉 எதிர்மறை செய்தி அழுத்தம் (Bearish Extension)"
            estimated_target = current_price * 0.988  # -1.2% சரிவு இலக்கு
        else:
            prediction = "💤 சாதாரண டிரெண்ட் (Neutral Market)"
            estimated_target = current_price

        return {
            "கம்பெனி": clean_ticker,
            "நேரடி விலை (₹)": round(current_price, 2),
            "செய்தி சென்டிமென்ட்": prediction,
            "கணிக்கப்பட்ட இலக்கு விலை (₹)": round(estimated_target, 2),
            "ஆராய்ந்த செய்திகள்": news_count
        }
    except:
        return {"சிக்னல்": "எரர் ⚠️", "டார்கெட்": 0.0}

