#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests
from datetime import datetime

# 📄 ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")

# ✅ ตรึงหัวเรื่องไว้ด้านบน เลื่อนลง ~5cm และจัดกลาง
st.markdown("""
    <div style="position: fixed; top: 40px; left: 0; width: 100%; background-color: #ffffff;
                display: flex; justify-content: center; align-items: center;
                padding: 1rem 1.5rem; font-size: 24px; font-weight: bold; color: #333;
                z-index: 1000; border-bottom: 1px solid #ddd;">
        🤖 Junior Chatbot
    </div>
    <div style="margin-top: 250px;"></div>
""", unsafe_allow_html=True)

# 🌐 ตั้งค่า Groq API
API_KEY = "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"  # 👈 ใส่ API Key ของคุณ
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 🌟 system message
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ "
        "เมื่อเริ่มต้นการสนทนา ให้แนะนำตัวว่า "
        "'สวัสดีครับ! ฉันชื่อ junior Chatbot ผู้ช่วยที่พร้อมจะตอบคำถามและช่วยเหลือคุณในเรื่องต่างๆ'"
    )
}

# 📦 เตรียม session state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "แชทใหม่"

if st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat] = [SYSTEM_MESSAGE]

if "renaming" not in st.session_state:
    st.session_state.renaming = None

# 📂 Sidebar
st.sidebar.title("📂 หัวข้อแชท")

# ➕ เริ่มแชทใหม่
if st.sidebar.button("➕ เริ่มแชทใหม่"):
    new_title = f"แชทเมื่อ {datetime.now().strftime('%H:%M:%S')}"
    st.session_state.all_chats[new_title] = [SYSTEM_MESSAGE]
    st.session_state.current_chat = new_title
    st.rerun()

# 🔁 แสดงรายการหัวข้อทั้งหมด พร้อม highlight หัวข้อปัจจุบัน
for title in list(st.session_state.all_chats.keys()):
    is_selected = title == st.session_state.current_chat
    button_style = (
        "background-color: #cce5ff; font-weight: bold; border-radius: 5px; padding: 0.4rem;"
        if is_selected else
        "background-color: transparent; padding: 0.4rem;"
    )

    col1, col2, col3 = st.sidebar.columns([6, 1, 1])

    # 📝 ปุ่มเลือกหัวข้อพร้อม highlight
    if col1.button(f"{title}", key=f"title-{title}"):
        st.session_state.current_chat = title
        st.session_state.renaming = None
        st.rerun()

    # ✏️ เปลี่ยนชื่อหัวข้อ
    if col2.button("✏️", key=f"edit-{title}"):
        st.session_state.renaming = title
        st.rerun()

    # 🗑️ ลบหัวข้อ
    if col3.button("🗑️", key=f"delete-{title}"):
        del st.session_state.all_chats[title]
        if title == st.session_state.current_chat:
            st.session_state.current_chat = next(iter(st.session_state.all_chats), "แชทใหม่")
        st.rerun()

# 📝 ช่องเปลี่ยนชื่อหัวข้อ
if st.session_state.renaming == st.session_state.current_chat:
    new_name = st.sidebar.text_input("เปลี่ยนชื่อหัวข้อ", value=st.session_state.current_chat)
    if st.sidebar.button("✅ ยืนยันการเปลี่ยนชื่อ"):
        old_name = st.session_state.current_chat
        if new_name and new_name != old_name:
            st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(old_name)
            st.session_state.current_chat = new_name
        st.session_state.renaming = None
        st.rerun()

# 💬 โหลดบทสนทนาหัวข้อปัจจุบัน
chat_history = st.session_state.all_chats[st.session_state.current_chat]

# 🧾 แสดงประวัติการคุย
for msg in chat_history[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 📥 รับ input จากผู้ใช้
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


