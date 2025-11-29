import streamlit as st
import pandas as pd
from google import genai

st.title("😆 Punbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses using puns. "
    "To use this app, you need to provide a Gemini API key, which you can get here: https://aistudio.google.com/app/apikey "
)

gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    client = genai.Client(api_key=gemini_api_key)

    MODEL_NAME = "gemini-2.5-flash"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question and the bot will respond with a pun!"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        conversation_text = (
            "You are Punbot, a chatbot that always answers with witty, humorous puns.\n\n"
        )

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                conversation_text += f"User: {msg['content']}\n"
            else:
                conversation_text += f"Punbot: {msg['content']}\n"

        conversation_text += "Punbot: "

        stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=conversation_text
        )

        with st.chat_message("assistant"):
            container = st.empty()
            full_response = ""

            for chunk in stream:
                if hasattr(chunk, "text") and chunk.text:
                    full_response += chunk.text
                    container.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

    if st.session_state.messages:
        df = pd.DataFrame(st.session_state.messages)
        st.write("### Conversation History")
        st.dataframe(df)

        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Conversation History as CSV",
            data=csv,
            file_name="punbot_conversation_history.csv",
            mime="text/csv"
        )
