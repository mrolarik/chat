#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests
from datetime import datetime

# 🌐 CONFIG
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")
API_KEY = "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"  # 👈 เปลี่ยนตรงนี้
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 🌟 system prompt
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ "
        "เมื่อเริ่มต้นการสนทนา ให้แนะนำตัวว่า "
        "'สวัสดีครับ! ฉันชื่อ junior Chatbot ผู้ช่วยที่พร้อมจะตอบคำถามและช่วยเหลือคุณในเรื่องต่างๆ'"
    )
}

# 📦 Session state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "แชทใหม่"

if st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat] = [SYSTEM_MESSAGE]

# 📂 Sidebar
st.sidebar.title("📂 หัวข้อแชท")

# ➕ สร้างแชทใหม่
if st.sidebar.button("➕ เริ่มแชทใหม่"):
    new_title = f"แชทเมื่อ {datetime.now().strftime('%H:%M:%S')}"
    st.session_state.all_chats[new_title] = [SYSTEM_MESSAGE]
    st.session_state.current_chat = new_title
    st.rerun()

# ✏️ ตัวแปรช่วยเปลี่ยนชื่อ
if "renaming" not in st.session_state:
    st.session_state.renaming = None

# 🔁 แสดงรายการหัวข้อ
for title in list(st.session_state.all_chats.keys()):
    col1, col2, col3 = st.sidebar.columns([6, 1, 1])

    # 📝 คลิกเพื่อเปลี่ยนหัวข้อ
    if col1.button(title, key=f"title-{title}"):
        st.session_state.current_chat = title
        st.session_state.renaming = None
        st.rerun()

    # ✏️ แสดงฟอร์มเปลี่ยนชื่อ
    if title == st.session_state.current_chat and st.session_state.renaming == title:
        new_name = st.sidebar.text_input("เปลี่ยนชื่อแชท", value=title, key="rename_input")
        if st.sidebar.button("✅ ยืนยันการเปลี่ยนชื่อ"):
            if new_name and new_name != title:
                st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(title)
                st.session_state.current_chat = new_name
            st.session_state.renaming = None
            st.rerun()
    elif col2.button("✏️", key=f"edit-{title}"):
        st.session_state.renaming = title
        st.rerun()

    # 🗑️ ลบหัวข้อ
    if col3.button("🗑️", key=f"delete-{title}"):
        del st.session_state.all_chats[title]
        if title == st.session_state.current_chat:
            st.session_state.current_chat = next(iter(st.session_state.all_chats), "แชทใหม่")
        st.rerun()

# 🎯 โหลดแชทปัจจุบัน
chat_history = st.session_state.all_chats[st.session_state.current_chat]

# 📜 แสดงประวัติการสนทนา
for msg in chat_history[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 💬 รับ input ใหม่
if user_input := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    chat_history.append({"role": "user", "content": user_input})

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
                error_message = res_json.get("error", {}).get("message", "เกิดข้อผิดพลาดจาก API")
                reply = f"❌ ไม่สามารถประมวลผลได้: {error_message}"

        except Exception as e:
            reply = f"❌ ข้อผิดพลาดขณะเชื่อมต่อ: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)
    chat_history.append({"role": "assistant", "content": reply})
