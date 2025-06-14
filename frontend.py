# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv

load_dotenv()

# Step1: Setup UI with streamlit (model provider, model, system prompt, web_search, query)
import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration with custom styling
st.set_page_config(
    page_title="LangGraph Agent UI",
    layout="centered",
    page_icon="🤖",
    initial_sidebar_state="collapsed",
)

# Custom CSS for attractive styling
st.markdown(
    """
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stTitle {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem !important;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #2E86AB, #A23B72, #F18F01);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #2E86AB;
        box-shadow: 0 0 10px rgba(46, 134, 171, 0.3);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    .stRadio > div {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .stCheckbox > div {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #2E86AB, #A23B72) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4) !important;
    }
    
    .response-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .response-text {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #F18F01;
        backdrop-filter: blur(10px);
    }
    
    .download-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .section-header {
        color: #2E86AB;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2E86AB;
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .config-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header section
st.title("🤖 AI Chatbot Agents")
st.markdown(
    '<p class="subtitle">Create and Interact with Intelligent AI Agents!</p>',
    unsafe_allow_html=True,
)

# Configuration section
st.markdown('<div class="config-section">', unsafe_allow_html=True)
st.markdown(
    '<div class="section-header">🔧 Agent Configuration</div>', unsafe_allow_html=True
)

# Create columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    system_prompt = st.text_area(
        "🎯 Define your AI Agent:",
        height=70,
        placeholder="Type your system prompt here... (e.g., 'You are a helpful assistant specialized in...')",
        help="Define the personality and expertise of your AI agent",
    )

with col2:
    st.markdown(
        '<div class="info-box">💡 Tip: Be specific about your agent\'s role and expertise for better results!</div>',
        unsafe_allow_html=True,
    )

# Model selection section
col3, col4 = st.columns(2)

MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

with col3:
    provider = st.radio(
        "🔌 Select Provider:",
        ("Groq", "OpenAI"),
        help="Choose your preferred AI model provider",
    )

with col4:
    if provider == "Groq":
        selected_model = st.selectbox(
            "🧠 Select Groq Model:",
            MODEL_NAMES_GROQ,
            help="Choose the Groq model for your agent",
        )
    elif provider == "OpenAI":
        selected_model = st.selectbox(
            "🧠 Select OpenAI Model:",
            MODEL_NAMES_OPENAI,
            help="Choose the OpenAI model for your agent",
        )

# Web search option
allow_web_search = st.checkbox(
    "🌐 Allow Web Search", help="Enable web search capabilities for your agent"
)

st.markdown("</div>", unsafe_allow_html=True)

# Query section
st.markdown('<div class="section-header">💬 Your Query</div>', unsafe_allow_html=True)
user_query = st.text_area(
    "Enter your query:",
    height=150,
    placeholder="Ask anything! Your AI agent is ready to help...",
    label_visibility="collapsed",
)

API_URL = "https://ai-chatbot-agents-goav.onrender.com/messages"

# Center the button
col_center = st.columns([1, 2, 1])
with col_center[1]:
    ask_button = st.button("🚀 Ask Agent!", use_container_width=True)

# Store response in session state to persist it
if "agent_response" not in st.session_state:
    st.session_state.agent_response = None
if "response_timestamp" not in st.session_state:
    st.session_state.response_timestamp = None

if ask_button:
    if user_query.strip():
        with st.spinner("🤔 Your AI agent is thinking..."):
            try:
                payload = {
                    "model_name": selected_model,
                    "model_provider": provider,
                    "system_prompt": system_prompt,
                    "messages": [user_query],
                    "allow_search": allow_web_search,
                }

                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    response_data = response.json()
                    if "error" in response_data:
                        st.error(f"❌ Error: {response_data['error']}")
                    else:
                        st.session_state.agent_response = response_data
                        st.session_state.response_timestamp = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        st.success("✅ Response received successfully!")
                else:
                    st.error(
                        f"❌ Request failed with status code: {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a query before asking the agent!")

# Display response if available
if st.session_state.agent_response:
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    st.markdown("### 🤖 Agent Response")
    st.markdown(
        f'<div class="response-text">{st.session_state.agent_response}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**📅 Generated:** {st.session_state.response_timestamp}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Download section
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.markdown("### 📥 Download Response")

    # Prepare download data
    download_data = {
        "timestamp": st.session_state.response_timestamp,
        "configuration": {
            "provider": provider,
            "model": selected_model,
            "system_prompt": system_prompt,
            "web_search_enabled": allow_web_search,
        },
        "query": user_query,
        "response": st.session_state.agent_response,
    }

    # Create columns for download options
    download_col1, download_col2 = st.columns(2)

    with download_col1:
        # JSON download
        json_data = json.dumps(download_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download as JSON",
            data=json_data,
            file_name=f"ai_agent_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

    with download_col2:
        # Text download
        text_data = f"""AI Agent Response
================

Generated: {st.session_state.response_timestamp}

Configuration:
- Provider: {provider}
- Model: {selected_model}
- System Prompt: {system_prompt}
- Web Search: {'Enabled' if allow_web_search else 'Disabled'}

Query:
{user_query}

Response:
{st.session_state.agent_response}
"""
        st.download_button(
            label="📝 Download as Text",
            data=text_data,
            file_name=f"ai_agent_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">Made with ❤️ using Streamlit | AI-Powered Conversations</div>',
    unsafe_allow_html=True,
)
