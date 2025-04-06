#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests
from datetime import datetime

# 🌐 CONFIG
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")
API_KEY = "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"  # 👈 เปลี่ยนตรงนี้
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 📌 สร้าง dictionary เพื่อเก็บทุก session ของแชท
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

# 📌 เก็บชื่อหัวข้อปัจจุบัน
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "แชทใหม่"

# 🧠 Sidebar สำหรับเลือกหรือสร้างหัวข้อ
st.sidebar.title("📂 หัวข้อแชท")
chat_titles = list(st.session_state.all_chats.keys())

selected_chat = st.sidebar.selectbox(
    "เลือกหัวข้อ",
    ["แชทใหม่"] + chat_titles,
    index=0 if st.session_state.current_chat == "แชทใหม่" else chat_titles.index(st.session_state.current_chat) + 1,
)

if selected_chat != st.session_state.current_chat:
    st.session_state.current_chat = selected_chat

# 🆕 ปุ่มเริ่มแชทใหม่
if st.sidebar.button("➕ เริ่มหัวข้อใหม่"):
    new_title = f"แชทเมื่อ {datetime.now().strftime('%H:%M:%S')}"
    st.session_state.all_chats[new_title] = [
        {
            "role": "system",
            "content": (
                "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ "
                "เมื่อเริ่มต้นการสนทนา ให้แนะนำตัวว่า "
                "'สวัสดีครับ! ฉันชื่อ junior Chatbot ผู้ช่วยที่พร้อมจะตอบคำถามและช่วยเหลือคุณในเรื่องต่างๆ'"
            )
        }
    ]
    st.session_state.current_chat = new_title

# 📂 ดึงประวัติของหัวข้อปัจจุบัน
if st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat] = [
        {
            "role": "system",
            "content": (
                "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ "
                "เมื่อเริ่มต้นการสนทนา ให้แนะนำตัวว่า "
                "'สวัสดีครับ! ฉันชื่อ junior Chatbot ผู้ช่วยที่พร้อมจะตอบคำถามและช่วยเหลือคุณในเรื่องต่างๆ'"
            )
        }
    ]

chat_history = st.session_state.all_chats[st.session_state.current_chat]

# 🔁 แสดงประวัติการสนทนา
for msg in chat_history[1:]:  # ข้าม system message
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 📩 รอรับข้อความใหม่
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

        response = requests.post(API_URL, headers=headers, json=payload)
        reply = response.json()["choices"][0]["message"]["content"]

    with st.chat_message("assistant"):
        st.markdown(reply)
    chat_history.append({"role": "assistant", "content": reply})
