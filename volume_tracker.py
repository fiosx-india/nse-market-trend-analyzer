import pandas as pd

def check_bulk_deals(df):
    try:
        # வால்யூம் தரவு இருந்தால் பல்க் டீல் ஸ்கேன் செய்யும் லாஜிக்
        if 'Volume' in df.columns and len(df) > 30:
            avg_volume = df['Volume'].iloc[-30:-1].mean()
            current_volume = df['Volume'].iloc[-1]
            
            # கடந்த 1 மணிநேர சராசரியை விட 3 மடங்கு வால்யூம் எகிறினால் அது பல்க் டீல்!
            if current_volume > (avg_volume * 3):
                return "⚠️ பல்க் டீல் / மெகா ஆர்டர்!"
            elif current_volume > (avg_volume * 1.5):
                return "📈 நல்ல வால்யூம் சேர்க்கை"
        return "சாதாரண வர்த்தகம்"
    except:
        return "சாதாரண வர்த்தகம்"

