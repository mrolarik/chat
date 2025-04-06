import streamlit as st
from transformers import pipeline

# สร้าง Chatbot pipeline โดยใช้โมเดล pre-trained
chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

st.set_page_config(page_title="Chatbot by Streamlit", page_icon="💬")
st.title("🤖 Chatbot ตัวอย่าง")

# เก็บประวัติการสนทนา
if "history" not in st.session_state:
    st.session_state.history = []

# รับข้อความจากผู้ใช้
user_input = st.text_input("คุณ: ", key="input")

if user_input:
    from transformers import ConversationalPipeline, Conversation
    conversation = Conversation(user_input)
    result = chatbot(conversation)
    bot_response = result.generated_responses[-1]
    
    # บันทึกประวัติการคุย
    st.session_state.history.append(("คุณ", user_input))
    st.session_state.history.append(("บอท", bot_response))

# แสดงประวัติการคุยย้อนหลัง
for speaker, text in st.session_state.history:
    st.write(f"**{speaker}**: {text}")
