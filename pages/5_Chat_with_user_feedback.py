import streamlit as st
import openai
from trubrics.integrations.streamlit import FeedbackCollector


with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="langchain_search_api_key_openai", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    
st.title("🔎 Dr.Bob - Chat with me")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, how can I help you? 你好，有什么我可以帮你的嘛？"}
    ]
if "response" not in st.session_state:
    st.session_state["response"] = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

model = "gpt-3.5-turbo"

if prompt := st.chat_input(placeholder="Tell me a joke about sharks"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(model=model, messages=st.session_state.messages)
    st.session_state["response"] = response.choices[0].message.content
    with st.chat_message("assistant"):
        st.session_state.messages.append({"role": "assistant", "content": st.session_state["response"]})
        st.write(st.session_state["response"])

if st.session_state["response"]:
    collector = FeedbackCollector(
        component_name="default",
        email=st.secrets.get("TRUBRICS_EMAIL"),
        password=st.secrets.get("TRUBRICS_PASSWORD")
    )

    feedback = collector.st_feedback(
        feedback_type="thumbs",
        model=model,
        open_feedback_label="[Optional] Provide additional feedback",
        metadata={"chat": st.session_state.messages},
        save_to_trubrics=True if st.secrets.get("TRUBRICS_SAVE") else False,
    )
    if feedback and st.secrets.get("TRUBRICS_SAVE") is None:
        st.success("Feedback saved! You can analyse your feedback with https://trubrics.streamlit.app/.")
