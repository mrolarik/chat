#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests
from datetime import datetime
import random
import re
from PyPDF2 import PdfReader
import pandas as pd

# 🌐 ตั้งค่า Streamlit
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")

# 🔐 Groq API
API_KEY = "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"  # 👉 เปลี่ยนตรงนี้
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 🧠 SYSTEM MESSAGE
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ ตอบคำถามตามที่ผู้ใช้ถาม"
}

# 📆 เตรียม session state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "chat_files" not in st.session_state:
    st.session_state.chat_files = {}

if "chat_summaries" not in st.session_state:
    st.session_state.chat_summaries = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "แชทใหม่"

if st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat] = [SYSTEM_MESSAGE]

if "renaming" not in st.session_state:
    st.session_state.renaming = None

# 🔹 Header Sidebar
st.sidebar.title("🤖 Junior Chatbot")
st.sidebar.markdown("---")
st.sidebar.markdown("📂 หัวข้อแชท", unsafe_allow_html=True)

if st.sidebar.button("➕ เริ่มแชทใหม่"):
    new_title = f"แชทเมื่อ {datetime.now().strftime('%H:%M:%S')}"
    st.session_state.all_chats[new_title] = [SYSTEM_MESSAGE]
    st.session_state.current_chat = new_title
    st.session_state.last_user_msg = ""
    st.rerun()

for title in list(st.session_state.all_chats.keys()):
    is_selected = title == st.session_state.current_chat
    col1, col2, col3 = st.sidebar.columns([6, 1, 1])
    if col1.button(f"{title}", key=f"title-{title}"):
        st.session_state.current_chat = title
        st.session_state.renaming = None
        st.rerun()
    if col2.button("✏️", key=f"edit-{title}"):
        st.session_state.renaming = title
        st.rerun()
    if col3.button("🗑️", key=f"delete-{title}"):
        del st.session_state.all_chats[title]
        st.session_state.chat_files.pop(title, None)
        st.session_state.chat_summaries.pop(title, None)
        if title == st.session_state.current_chat:
            st.session_state.current_chat = next(iter(st.session_state.all_chats), "แชทใหม่")
        st.rerun()

# เปลี่ยนชื่อหัวข้อ
if st.session_state.renaming == st.session_state.current_chat:
    new_name = st.sidebar.text_input("เปลี่ยนชื่อหัวข้อ", value=st.session_state.current_chat)
    if st.sidebar.button("✅ ยืนยันการเปลี่ยนชื่อ"):
        old = st.session_state.current_chat
        if new_name and new_name != old:
            st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(old)
            st.session_state.chat_files[new_name] = st.session_state.chat_files.pop(old, "")
            st.session_state.chat_summaries[new_name] = st.session_state.chat_summaries.pop(old, {})
            st.session_state.current_chat = new_name
        st.session_state.renaming = None
        st.rerun()

# 📜 โหลดประวัติแชท
chat_id = st.session_state.current_chat
chat_history = st.session_state.all_chats[chat_id]

# 📂 อัปโหลดไฟล์
st.markdown("#### 📎 อัปโหลดไฟล์ (PDF หรือ CSV) สำหรับหัวข้อนี้")
uploaded_files = st.file_uploader("เลือกไฟล์", type=["pdf", "csv"], accept_multiple_files=True, key=chat_id)

summaries = {}
all_text = ""

if uploaded_files:
    st.markdown("#### 🧠 สรุปใจความสำคัญของไฟล์ที่อัปโหลด")
    for file in uploaded_files:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file.name.endswith(".csv"):
            df = pd.read_csv(file)
            text = df.to_string(index=False)
        else:
            text = ""

        all_text += f"\n--- จากไฟล์: {file.name} ---\n{text[:3000]}\n"

        with st.spinner(f"🤖 กำลังสรุป {file.name}..."):
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "คุณคือผู้ช่วยที่เก่งในการสรุปเอกสารเป็นภาษาไทยแบบกระชับและเข้าใจง่าย"
                    },
                    {
                        "role": "user",
                        "content": (
                            "กรุณาสรุปเนื้อหาสำคัญของไฟล์ต่อไปนี้ **เป็นภาษาไทย** โดยให้สั้น กระชับ ชัดเจน "
                            "หากเป็นข้อมูลตารางให้แสดงภาพรวมที่เข้าใจง่าย:\n\n"
                            f"{text[:3000]}"
                        )
                    }
                ],
                "temperature": 0.3,
            }
            try:
                res = requests.post(API_URL, headers=headers, json=payload)
                summary = res.json()["choices
