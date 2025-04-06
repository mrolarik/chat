#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests
from datetime import datetime

# 🌐 CONFIG
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")
API_KEY = "your-groq-api-key"  # 👈 ใส่ API Key จาก https://console.groq.com/keys
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 🧠 ค่าเริ่มต้นสำหรับระบบ
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ "
        "เมื่อเริ่มต้นการสนทนา ให้แนะนำตัวว่า "
        "'สวัสดีครับ! ฉันชื่อ junior Chatbot ผู้ช่วยที่พร้อมจะตอบคำถามและช่วยเหลือคุณในเรื่องต่างๆ'"
    )
}

# 🗃️ สร้างโครงสร้างเก็บหัวข้อแชทและสถานะปัจจุบัน
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "แชทใหม่"

# 📌 เริ่ม Sidebar
st.sidebar.title("📂 หัวข้อแชท")

# ➕ ปุ่มเริ่มแชทใหม่
if st.sidebar.button("➕ เริ่มแชทใหม่"):
    new_title = f"แชทเมื่อ {datetime.now().strftime('%H:%M:%S')}"
    st.session_state.all_chats[new_title] = [SYSTEM_MESSAGE]
    st.session_state.current_chat = new_title
    st.rerun()

# 🔘 แสดงทุกหัวข้อเป็นปุ่ม
for title in st.session_state.all_chats.keys():
    if st.sidebar.button(title):
        st.session_state.current_chat = title
        st.rerun()

# 📥 หากยังไม่มีหัวข้อนี้ใน all_chats ให้สร้างใหม่
if st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat] = [SYSTEM_MESSAGE]

# ✅ โหลดประวัติของหัวข้อปัจจุบัน
chat_history = st.session_state.all_chats[st.session_state.current_chat]

# 📜 แสดงบทสนทนาย้อนหลัง
for msg in chat_history[1:]:  # ข้าม system message
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 💬 รับ input ใหม่
if user_input := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    chat_history.append({"role": "user", "content": user_input})

    # 🔄 เรียก Groq API
    with st.spinner("กำลังคิดคำตอบ..."):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MODEL,
            "messages": chat_history,
            "temperature": 0.7,
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            res_json = response.json()

            if "choices" in res_json:
                reply = res_json["choices"][0]["message"]["content"]
            else:
                error_message = res_json.get("error", {}).get("message", "เกิดข้อผิดพลาดบางอย่างจาก API")
                reply = f"❌ ไม่สามารถประมวลผลได้: {error_message}"

        except Exception as e:
            reply = f"❌ ข้อผิดพลาดขณะเชื่อมต่อ: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)

    chat_history.append({"role": "assistant", "content": reply})
