import streamlit as st
from groq import Groq
import os, tempfile
 
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
 

st.title("🤖 My Chatbot")
 
if "messages" not in st.session_state:
    st.session_state.messages = []
 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
 
if prompt := st.chat_input("اكتبي سؤالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            try:
                messages = [{"role": "system", "content": "You are a helpful assistant."}]
                for msg in st.session_state.messages:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                response = client.chat.completions.create(
                    # model="llama-3.3-70b-versatile",
                    model="openai/gpt-oss-120b",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"خطأ: {str(e)}"
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
 
 

st.markdown("---")
st.markdown("### تحدث بدلاً من الكتابة")
 
audio = st.audio_input("سجّل سؤالك...")
 
if audio:
    if st.button("أرسل الصوت "):
        # تحويل الصوت إلى نص
        with st.spinner("جاري تحويل صوتك إلى نص..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio.read())
                path = tmp.name
            try:
                with open(path, "rb") as f:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=(os.path.basename(path), f),
                        response_format="text"
                    )
            finally:
                os.unlink(path)
 
        if not transcript or len(transcript.strip()) < 2:
            st.error("لم يتم التعرف على الصوت، حاول مرة أخرى!")
        else:
            # إضافة سؤال المستخدم للمحادثة
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(f" {transcript}")
 
            # الحصول على رد الـ Chatbot
            with st.chat_message("assistant"):
                with st.spinner("جاري التفكير..."):
                    try:
                        messages = [{"role": "system", "content": "You are a helpful assistant."}]
                        for msg in st.session_state.messages:
                            messages.append({"role": msg["role"], "content": msg["content"]})
                        response = client.chat.completions.create(
                            # model="llama-3.3-70b-versatile",
                            model="openai/gpt-oss-120b",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                        answer = response.choices[0].message.content
                    except Exception as e:
                        answer = f"خطأ: {str(e)}"
                st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
