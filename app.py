import streamlit as st
from transformers import pipeline

# ใช้ text-generation แทน conversational
generator = pipeline("text-generation", model="gpt2")

st.set_page_config(page_title="Chatbot แบบง่าย", page_icon="🤖")
st.title("🤖 Chatbot ตัวอย่าง")

if "history" not in st.session_state:
    st.session_state.history = []

# รับข้อความจากผู้ใช้
user_input = st.text_input("คุณ: ", key="input")

if user_input:
    # รวมข้อความที่เคยพูดไว้เพื่อส่งเข้าโมเดล
    prompt = "\n".join([f"{speaker}: {text}" for speaker, text in st.session_state.history])
    prompt += f"\nคุณ: {user_input}\nบอท:"

    # ใช้โมเดลสร้างคำตอบ
    response = generator(prompt, max_length=100, do_sample=True, temperature=0.7)[0]["generated_text"]
    
    # ตัดเอาเฉพาะคำตอบหลังคำว่า 'บอท:'
    bot_reply = response.split("บอท:")[-1].strip().split("\n")[0]

    # บันทึกประวัติ
    st.session_state.history.append(("คุณ", user_input))
    st.session_state.history.append(("บอท", bot_reply))

# แสดงบทสนทนา
for speaker, text in st.session_state.history:
    st.write(f"**{speaker}**: {text}")
