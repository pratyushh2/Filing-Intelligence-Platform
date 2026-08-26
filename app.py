import streamlit as st
import requests

st.title("Filing Intelligence")
st.write("Ask a question about Apple's latest 10-K risk factors")

question = st.text_input("Your question")

if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"text": question}
            )
            answer = response.json()["answer"]
        st.write(answer)
    else:
        st.warning("Type a question first")