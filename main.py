import requests
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_card as stcard

from pypdf import PdfReader

import logging

logging.basicConfig(level=logging.INFO)

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

# Initialize session state variables
if 'conversation_results' not in st.session_state:
    st.session_state.conversation_results = {
        "Discover Your Strengths & Weaknesses": "",
        "Resume Review": "",
        "Academic Background": "",
        "Career Advice": ""
    }

if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

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

def query_flowise(question, api_url, bot_type='general', override_config_text=None):
    try:
        if override_config_text:
            if bot_type == 'resume':
                payload = {
                    "question": question,
                    "overrideConfig": {"text": override_config_text}
                }
            elif bot_type == 'advice':
                payload = {
                    "question": question,
                    "overrideConfig": {"profile": override_config_text}
                }
        else:
             payload = {
                "question": question,
            }

        logging.info(f"Sending request to {api_url} with payload: {payload}")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        result = response.json()
        logging.info(f"Received response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in API request: {e}")
        return {"text": f"An error occurred: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"text": "An unexpected error occurred"}
    

def query_flowise_resume(question, api_url, resume_text):
    try:
        payload = {
            "question": question,
            "overrideConfig": {"text": resume_text}
        }
        logging.info(f"Sending request to {api_url} with payload: {payload}")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        result = response.json()
        logging.info(f"Received response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in API request: {e}")
        return {"text": f"An error occurred: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"text": "An unexpected error occurred"}
    
def query_flowise_advice(question, api_url, profile_info):
    try:
        payload = {
            "question": question,
            "overrideConfig": {"profile": profile_info}
        }
        logging.info(f"Sending request to {api_url} with payload: {payload}")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        logging.info(f"Received response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in API request: {e}")
        return {"text": f"An error occurred: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"text": "An unexpected error occurred"}

def display_chatbot(title, description, api_url=None, bot_type='general', extra_data=None, initial_message=None):
    st.header(title)
    st.write(description)

    # Initialize chat history
    if f"{title}_messages" not in st.session_state:
        st.session_state[f"{title}_messages"] = []

        # If there's an initial message (like the resume text), send it automatically
        if initial_message:
            # Process the initial message as if it's a user input
            process_user_input(title, initial_message, api_url, bot_type, extra_data)
    
    # Display chat messages from history
    for message in st.session_state[f"{title}_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Placeholder for input field
    input_placeholder = st.empty()

    # Render the input field inside the placeholder
    user_input = input_placeholder.text_input("Your message:", key=f"{title}_input")

    # Send button logic
    if st.button("Send", key=f"{title}_send"):
        if user_input:
            process_user_input(title, user_input, api_url, bot_type, extra_data)
            # Clear the input field after sending a message by re-rendering the placeholder
            input_placeholder.empty()
            st.rerun()

    # Clear Chat and Finish Conversation buttons at the bottom
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Clear Chat", key=f"{title}_clear"):
            st.session_state[f"{title}_messages"] = []
            st.session_state.conversation_results[title] = ""
            st.rerun()
    with col2:
        if st.button("Finish Conversation", key=f"{title}_finish"):
            st.success(f"Conversation for {title} finished. You can now move to the next section.")




def process_user_input(title, user_input, api_url, bot_type, extra_data):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state[f"{title}_messages"].append({"role": "user", "content": user_input})

    # Generate and display AI response
    with st.chat_message("assistant"):
        response = query_flowise(user_input, api_url, bot_type, override_config_text=extra_data)
        ai_response = response.get('text', 'Sorry, I couldn\'t process that.')
        st.markdown(ai_response)
    st.session_state[f"{title}_messages"].append({"role": "assistant", "content": ai_response})

    # Save the conversation summary
    if title not in st.session_state.conversation_results:
        st.session_state.conversation_results[title] = ""
    st.session_state.conversation_results[title] += f"\nUser: {user_input}\nAI: {ai_response}"


# Define API URLs
STRENGTHS_WEAKNESSES_API = "https://finflowise.onrender.com/api/v1/prediction/0113af8b-95c9-438f-b3fd-6db650058e9c"
ACADEMIC_BACKGROUND_API = "https://finflowise.onrender.com/api/v1/prediction/7f1cc35a-bc96-4f85-a1f4-f8fceaca63f1"
RESUME_API_URL = "https://finflowise.onrender.com/api/v1/prediction/491fa248-427b-417e-ab7d-6aac47ae20ff"
CAREER_ADVICE_API_URL = "https://finflowise.onrender.com/api/v1/prediction/031ba775-099b-491c-96ef-f0a7e45c72fa"

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
    st.header("Resume Review & Work Experience Analysis")
    st.write("Upload your resume and we'll analyze your past experiences to highlight your key skills.")

    uploaded_file = st.file_uploader("Choose your resume PDF file", type="pdf")
    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)
        resume_text = ''.join(page.extract_text() for page in reader.pages)
        st.success("Resume uploaded successfully!")
        st.write(resume_text)

        # Pass the resume_text as the initial message to the bot
        display_chatbot(
            "Resume Analysis",
            "Ask questions about your resume or request an analysis.",
            api_url=RESUME_API_URL,
            bot_type='resume',
            extra_data=resume_text,
            initial_message=f'My Resume:\n\n{resume_text}'  # Send the resume as the first message automatically
        )
    else:
        st.info("Please upload your resume to start the analysis.")


elif selected == "Academic Background":
    display_chatbot(
        "Academic Background",
        "Let's discuss your educational journey and academic interests.",
        api_url=ACADEMIC_BACKGROUND_API
    )

elif selected == "Career Advice":
    st.header("Personalized Career Recommendations")
    st.write("Based on your previous conversations, we'll provide personalized career advice.")

    # Combine all previous conversation results
    all_conversations = "\n\n".join([f"{key}:\n{value}" for key, value in st.session_state.conversation_results.items() if value])
    

    if all_conversations:
        st.write(all_conversations)
        display_chatbot(
            "Career Advice",
            "Ask for career advice based on your profile.",
            api_url=CAREER_ADVICE_API_URL,
            bot_type='advice',
            extra_data=all_conversations,
            initial_message=f'Here is my conversation with the other Chatbots:\n\n{all_conversations}'
        )
        
    else:
        st.warning("Please complete the other sections before seeking career advice.")

# Add a footer
st.markdown("---")
st.markdown("© 2024 AI Career Counselor. All rights reserved.")
