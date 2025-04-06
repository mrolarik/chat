#API_KEY = "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""  # 👉 เปลี่ยนตรงนี้

import streamlit as st
import requests

# ตั้งค่า Streamlit
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")
st.title("🤖 Chatbot ด้วย LLaMA3 + Groq API")

# กำหนด API Key และ Endpoint
API_KEY = "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"  # 👉 เปลี่ยนตรงนี้
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# เก็บประวัติการสนทนาใน session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "คุณคือผู้ช่วยที่เป็นมิตรและมีประโยชน์"}
    ]

# แสดงประวัติ
for msg in st.session_state.messages[1:]:  # ข้าม system message
    st.chat_message(msg["role"]).markdown(msg["content"])

# รับข้อความใหม่จากผู้ใช้
if user_input := st.chat_input("พิมพ์ข้อความของคุณที่นี่"):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # เรียก Groq API
    with st.spinner("กำลังคิด..."):
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

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
