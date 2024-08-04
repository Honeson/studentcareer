

import requests
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_card as stcard

st.set_page_config(page_title="Student Career Counselor", page_icon="🎓", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #175676;
    }
    .big-font {
        font-size: 24px !important;
    }
    .stButton>button {
        background-color: #4169E1;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 18px;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation using streamlit_option_menu
with st.sidebar:
    st.title("🎓 Student Counselor")
    selected = option_menu(
        menu_title="Navigation",
        options=[
            "Home", 
            "Strengths & Weaknesses", 
            "Resume Review", 
            "Academic Background", 
            "Career Advice"
        ],
        icons=[
            "house", 
            "person-check", 
            "file-earmark-text", 
            "book", 
            "briefcase"
        ],
        menu_icon="cast",
        default_index=0,
    )

# def query_flowise(question):
#     API_URL = "https://finflowise.onrender.com/api/v1/prediction/0113af8b-95c9-438f-b3fd-6db650058e9c"
#     response = requests.post(API_URL, json={"question": question})
#     return response.json()

def query_flowise(question, api_url):
    response = requests.post(api_url, json={"question": question})
    return response.json()


def display_chatbot(title, description, api_url=None):
    st.header(title)
    st.write(description)

    # Initialize chat history
    if f"{title}_messages" not in st.session_state:
        st.session_state[f"{title}_messages"] = []

    # Display chat messages from history
    for message in st.session_state[f"{title}_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Your message:", key=f"{title}_input")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        # Add user message to chat history
        st.session_state[f"{title}_messages"].append({"role": "user", "content": user_input})

        # Generate and display AI response
        with st.chat_message("assistant"):
            if api_url:
                response = query_flowise(user_input, api_url)
                ai_response = response.get('text', 'Sorry, I couldn\'t process that.')
            else:
                ai_response = "This chatbot is not yet implemented for this section."
            st.markdown(ai_response)
        # Add AI response to chat history
        st.session_state[f"{title}_messages"].append({"role": "assistant", "content": ai_response})

    # Clear chat button
    if st.button("Clear Chat", key=f"{title}_clear"):
        st.session_state[f"{title}_messages"] = []
        st.rerun()


# Define API URLs
STRENGTHS_WEAKNESSES_API = "https://finflowise.onrender.com/api/v1/prediction/0113af8b-95c9-438f-b3fd-6db650058e9c"
ACADEMIC_BACKGROUND_API = "https://finflowise.onrender.com/api/v1/prediction/7f1cc35a-bc96-4f85-a1f4-f8fceaca63f1"


if selected == "Home":
    st.title("Welcome to Student Career Counselor")
    st.markdown("<p class='big-font'>Discover your perfect career path with our AI-powered guidance.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        stcard.card(
            title="Explore Your Strengths",
            text="Uncover your unique abilities and talents.",
            image="https://img.icons8.com/color/96/000000/strength.png",
            url="#"
        )
    with col2:
        stcard.card(
            title="Analyze Your Experience",
            text="Get insights from your past work and projects.",
            image="https://img.icons8.com/color/96/000000/resume.png",
            url="#"
        )
    with col3:
        stcard.card(
            title="Plan Your Future",
            text="Receive personalized career recommendations.",
            image="https://img.icons8.com/color/96/000000/road.png",
            url="#"
        )

elif selected == "Strengths & Weaknesses":
    display_chatbot(
        "Discover Your Strengths & Weaknesses",
        "Let's explore your unique abilities and areas for growth.",
        api_url=STRENGTHS_WEAKNESSES_API
    )

elif selected == "Resume Review":
    display_chatbot(
        "Resume Review & Work Experience Analysis",
        "We'll analyze your past experiences to highlight your key skills."
    )

elif selected == "Academic Background":
    display_chatbot(
        "Academic Profile Assessment",
        "Let's discuss your educational journey and academic interests.",
        api_url=ACADEMIC_BACKGROUND_API
    )

elif selected == "Career Advice":
    display_chatbot(
        "Personalized Career Recommendations",
        "Based on your profile, we'll suggest suitable career paths."
    )

# Add a footer
st.markdown("---")
st.markdown("© 2024 AI Career Counselor. All rights reserved.")