import streamlit as st
import asyncio
import async_timeout

async def handle_with_timeout(async_function, timeout_seconds=5):
    try:
        async with async_timeout.timeout(timeout_seconds):
            return await async_function
    except asyncio.TimeoutError:
        return None
    except:
        return None

def display_safe_status(success_count, total_count):
    if success_count == total_count:
        st.success(f"✅ அத்தனை {total_count} கம்பெனிகளும் துல்லியமாக ஸ்கேன் செய்யப்பட்டு ரிப்போர்ட் தயார்!")
    elif success_count > 0:
        st.warning(f"⚠️ நெட்வொர்க் தாமதம் காரணமாக {success_count} / {total_count} பங்குகள் மட்டும் ஸ்கேன் செய்யப்பட்டுள்ளன...")
    else:
        st.error("❌ நெட்வொர்க் இணைப்பு துண்டிக்கப்பட்டுள்ளது. தயவுசெய்து இன்டர்நெட்டைச் சரிபார்க்கவும்!")
