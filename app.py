#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests
from datetime import datetime
import random
import re
from PyPDF2 import PdfReader
import pandas as pd

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")

# Header ตรึงบนสุด ตรงกลาง และเลื่อนลง ~5cm
st.markdown("""
    <div style="position: fixed; top: 40px; left: 0; width: 100%; background-color: #ffffff;
                display: flex; justify-content: center; align-items: center;
                padding: 1rem 1.5rem; font-size: 24px; font-weight: bold; color: #333;
                z-index: 1000; border-bottom: 1px solid #ddd;">
        🤖 Junior Chatbot
    </div>
    <div style="margin-top: 250px;"></div>
""", unsafe_allow_html=True)

# Groq API
API_KEY = "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"  # 👈 เปลี่ยนตรงนี้
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# SYSTEM MESSAGE พื้นฐาน
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ ตอบคำถามตามที่ผู้ใช้ถาม"
}

# ตั้งค่า session state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "chat_files" not in st.session_state:
    st.session_state.chat_files = {}  # เก็บข้อมูลจากไฟล์ต่อหัวข้อ

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "แชทใหม่"

if st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.all_chats[st.session_state.current_chat] = [SYSTEM_MESSAGE]

if "renaming" not in st.session_state:
    st.session_state.renaming = None

# Sidebar
st.sidebar.title("📂 หัวข้อแชท")

# ปุ่มเริ่มแชทใหม่
if st.sidebar.button("➕ เริ่มแชทใหม่"):
    new_title = f"แชทเมื่อ {datetime.now().strftime('%H:%M:%S')}"
    st.session_state.all_chats[new_title] = [SYSTEM_MESSAGE]
    st.session_state.current_chat = new_title
    st.session_state.last_user_msg = ""
    st.rerun()

# แสดงรายชื่อหัวข้อพร้อมปุ่ม
for title in list(st.session_state.all_chats.keys()):
    is_selected = title == st.session_state.current_chat
    button_style = (
        "background-color: #cce5ff; font-weight: bold; border-radius: 5px; padding: 0.4rem;"
        if is_selected else
        "background-color: transparent; padding: 0.4rem;"
    )

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
        if title == st.session_state.current_chat:
            st.session_state.current_chat = next(iter(st.session_state.all_chats), "แชทใหม่")
        st.rerun()

# เปลี่ยนชื่อหัวข้อ
if st.session_state.renaming == st.session_state.current_chat:
    new_name = st.sidebar.text_input("เปลี่ยนชื่อหัวข้อ", value=st.session_state.current_chat)
    if st.sidebar.button("✅ ยืนยันการเปลี่ยนชื่อ"):
        old_name = st.session_state.current_chat
        if new_name and new_name != old_name:
            st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(old_name)
            st.session_state.chat_files[new_name] = st.session_state.chat_files.pop(old_name, "")
            st.session_state.current_chat = new_name
        st.session_state.renaming = None
        st.rerun()

# โหลดบทสนทนา
chat_history = st.session_state.all_chats[st.session_state.current_chat]

# อัปโหลดไฟล์ PDF/CSV
st.markdown("#### 📎 อัปโหลดไฟล์ (PDF หรือ CSV) สำหรับหัวข้อนี้")
uploaded_file = st.file_uploader("เลือกไฟล์", type=["pdf", "csv"], key=st.session_state.current_chat)

if uploaded_file:
    file_text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        file_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_text = df.to_string(index=False)
    st.session_state.chat_files[st.session_state.current_chat] = file_text
    st.success("✅ อัปโหลดและแปลงไฟล์สำเร็จแล้ว")

# ตรวจภาษา
def is_english(text):
    return re.match(r'^[a-zA-Z0-9\s\.,!?]+$', text.strip()) is not None

# แนะนำตัวครั้งแรก
if len(chat_history) == 1:
    thai_greetings = [
        "สวัสดีครับ! ฉันคือ junior Chatbot 😊 ยินดีช่วยเหลือคุณทุกเรื่องเลยครับ",
        "สวัสดีครับ! ฉันชื่อ junior Chatbot 🤖 พร้อมช่วยคุณตอบคำถามทุกด้าน",
        "สวัสดีครับ! junior Chatbot อยู่ตรงนี้แล้วนะครับ 🙌 ถามมาได้เลย"
    ]
    eng_greetings = [
        "Hello! I am junior Chatbot 😊 How can I assist you today?",
        "Hi there! This is junior Chatbot 🤖 Ask me anything!",
        "Hey! I'm junior Chatbot 🙌 Ready to help!"
    ]
    last_user_message = st.session_state.get("last_user_msg", "")
    intro_message = random.choice(eng_greetings if is_english(last_user_message) else thai_greetings)
    with st.chat_message("assistant"):
        st.markdown(intro_message)
    chat_history.append({"role": "assistant", "content": intro_message})

# แสดงประวัติ
for msg in chat_history[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# รับข้อความผู้ใช้
if user_input := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    st.session_state.last_user_msg = user_input
    with st.chat_message("user"):
        st.markdown(user_input)
    chat_history.append({"role": "user", "content": user_input})

    # ใช้ข้อมูลจากไฟล์ (ถ้ามี)
    file_context = st.session_state.chat_files.get(st.session_state.current_chat, "")
    if file_context:
        system_instruction = {
            "role": "system",
            "content": f"""คุณจะได้รับข้อมูลจากเอกสารที่อัปโหลดดังนี้:\n\n{file_context[:3000]}\n\n
            โปรดตอบคำถามโดยอ้างอิงจากข้อมูลข้างต้นเท่านั้น หากไม่มีข้อมูลในเอกสารให้ตอบว่า "ไม่พบข้อมูลที่เกี่ยวข้องในเอกสาร"."""
        }
        full_messages = [system_instruction] + chat_history[1:]
    else:
        full_messages = chat_history

    with st.spinner("กำลังคิดคำตอบ..."):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {"model": MODEL, "messages": full_messages, "temperature": 0.7}

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

