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

# ✅ Header ตรึงบนสุดแบบตรงกลาง
#st.markdown("""
#    <div style="position: fixed; top: 189px; left: 0; width: 100%; background-color: #f0f2f6;
#                display: flex; justify-content: center; align-items: center;
#                padding: 1rem 1.5rem; font-size: 24px; font-weight: bold; color: #333;
#                z-index: 1000; border-bottom: 1px solid #ddd;">
#        🤖 Junior Chatbot
#    </div>
#    <div style="margin-top: 250px;"></div>
#""", unsafe_allow_html=True)

# 🔐 Groq API
API_KEY = "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"  # 👈 เปลี่ยนตรงนี้
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 🧠 SYSTEM MESSAGE
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ ตอบคำถามตามที่ผู้ใช้ถาม"
}

# 📦 เตรียม session state
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

# Sidebar Header
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

# ✏️ เปลี่ยนชื่อหัวข้อ
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

# 📜 โหลดบทสนทนา
chat_id = st.session_state.current_chat
chat_history = st.session_state.all_chats[chat_id]

# 📎 อัปโหลดไฟล์หลายไฟล์และสรุป
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

        # 🧠 สรุปใจความของไฟล์
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
                summary = res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                summary = f"❌ สรุปไม่ได้: {e}"

            summaries[file.name] = summary
            st.markdown(f"✅ **{file.name}**:\n\n{summary}")

    st.session_state.chat_files[chat_id] = all_text
    st.session_state.chat_summaries[chat_id] = summaries
    st.success("✅ อัปโหลดและสรุปไฟล์ทั้งหมดสำเร็จแล้ว")

# ✅ แสดงสรุปที่เคยอัปโหลด
#if chat_id in st.session_state.chat_summaries:
#    st.markdown("### 📄 สรุปไฟล์ที่อัปโหลดก่อนหน้า")
#    for fname, summary in st.session_state.chat_summaries[chat_id].items():
#        st.markdown(f"**{fname}**\n\n{summary}")

# ✅ ตรวจภาษา
def is_english(text):
    return re.match(r'^[a-zA-Z0-9\s\.,!?]+$', text.strip()) is not None

# 🤖 แนะนำตัวครั้งแรก
# แสดงแนะนำตัวเฉพาะเมื่อยังไม่มี assistant ตอบเลย
if len(chat_history) == 1 or not any(m["role"] == "assistant" for m in chat_history[1:]):
    with st.chat_message("assistant"):
        st.markdown(intro)
    chat_history.append({"role": "assistant", "content": intro})

# แสดงบทสนทนา
for msg in chat_history[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ✍️ รับข้อความผู้ใช้
if user_input := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    st.session_state.last_user_msg = user_input
    with st.chat_message("user"):
        st.markdown(user_input)
    chat_history.append({"role": "user", "content": user_input})

    # ใช้ข้อมูลจากไฟล์ (ถ้ามี)
    file_context = st.session_state.chat_files.get(chat_id, "")
    if file_context:
        sys_msg = {
            "role": "system",
            "content": f"""คุณจะได้รับข้อมูลจากเอกสารที่อัปโหลดดังนี้:\n\n{file_context[:3000]}\n\n
            โปรดตอบคำถามโดยอ้างอิงจากข้อมูลข้างต้นเท่านั้น หากไม่มีข้อมูลในเอกสารให้ตอบว่า "ไม่พบข้อมูลที่เกี่ยวข้องในเอกสาร"."""
        }
        full_messages = [sys_msg] + chat_history[1:]
    else:
        full_messages = chat_history

    with st.spinner("กำลังคิดคำตอบ..."):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {"model": MODEL, "messages": full_messages, "temperature": 0.7}

        try:
            res = requests.post(API_URL, headers=headers, json=payload)
            reply = res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"❌ ข้อผิดพลาดขณะเชื่อมต่อ: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)
    chat_history.append({"role": "assistant", "content": reply})


