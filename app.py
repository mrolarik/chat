#API_KEY = "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"  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests

# ตั้งค่า Streamlit
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")
st.title("🤖 junior Chatbot ด้วย LLaMA3 + Groq API")

# 🛠️ ตั้งค่า API Key และ Model
API_KEY = "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"  # ← เปลี่ยนเป็นของคุณ
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# 🌟 เริ่ม session ด้วย system message และบทนำ
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์ "
                "เมื่อเริ่มต้นการสนทนา ให้แนะนำตัวว่า "
                "'สวัสดีครับ! ฉันชื่อ junior Chatbot ผู้ช่วยที่พร้อมจะตอบคำถามและช่วยเหลือคุณในเรื่องต่างๆ'"
            )
        }
    ]

# 🔁 แสดงประวัติการสนทนาทั้งหมด
for msg in st.session_state.messages[1:]:  # ข้าม system message
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🧠 รอรับ input จากผู้ใช้
if user_input := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
    # แสดงคำถามของผู้ใช้
    with st.chat_message("user"):
        st.markdown(user_input)

    # บันทึกลงในประวัติ
    st.session_state.messages.append({"role": "user", "content": user_input})

    # เรียก API จาก Groq
    with st.spinner("กำลังคิดคำตอบ..."):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MODEL,
            "messages": st.session_state.messages,
            "temperature": 0.7,
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        reply = response.json()["choices"][0]["message"]["content"]

    # แสดงคำตอบจากบอท
    with st.chat_message("assistant"):
        st.markdown(reply)

    # บันทึกคำตอบลงในประวัติ
    st.session_state.messages.append({"role": "assistant", "content": reply})

