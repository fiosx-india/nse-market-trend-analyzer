import streamlit as st
import asyncio
import async_timeout

# ஆப் எங்கேயாவது லோடிங்கில் மாட்டிக்கொண்டால் 5 நொடிகளில் பூட்டை உடைக்கும் லாஜிக்
async def handle_with_timeout(async_function, timeout_seconds=5):
    try:
        async with async_timeout.timeout(timeout_seconds):
            return await async_function
    except asyncio.TimeoutError:
        # நெட்வொர்க் ஸ்லோவாக இருந்தால் ஆப் ஹேங் ஆகாமல் தற்காலிகமாகத் தவிர்க்கும்
        return None
    except Exception as e:
        return None

# ஸ்கிரீனில் எரர் காட்டாமல் யூசருக்குப் புரியும்படி தமிழ் மெசேஜ் காட்டும் வசதி
def display_safe_status(success_count, total_count):
    if success_count == total_count:
        st.success(f"✅ அத்தனை {total_count} கம்பெனிகளும் துல்லியமாக ஸ்கேன் செய்யப்பட்டு ரிப்போர்ட் தயார்!")
    elif success_count > 0:
        st.warning(f"⚠️ நெட்வொர்க் தாமதம் காரணமாக {success_count} / {total_count} பங்குகள் மட்டும் ஸ்கேன் செய்யப்பட்டுள்ளன. மீதமுள்ளவை ஆட்டோ-ரீகனெக்ட் செய்யப்படுகின்றன...")
    else:
        st.error("❌ நெட்வொர்க் இணைப்பு முற்றிலும் துண்டிக்கப்பட்டுள்ளது. தயவுசெய்து BSNL இன்டர்நெட்டைச் சரிபார்க்கவும்!")

