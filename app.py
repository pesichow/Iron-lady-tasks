import streamlit as st
import json
import os
from datetime import datetime
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import re

# Set up environment variables
os.environ["AZURE_OPENAI_API_KEY"] = "your api key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://genaideployment.openai.azure.com"
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4o"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# Sample data - in a real application, this would be in separate JSON files
faq_data = {
    "programs": [
        {
            "name": "Women in Leadership",
            "duration": "12 weeks",
            "format": "Online with weekly live sessions",
            "certificate": "Yes, upon completion",
            "mentors": ["Sarah Johnson", "Maria Rodriguez"]
        },
        {
            "name": "Executive Leadership Masterclass",
            "duration": "8 weeks",
            "format": "Hybrid (online + 2 in-person workshops)",
            "certificate": "Yes, with distinction levels",
            "mentors": ["Robert Chen", "Amanda Williams"]
        },
        {
            "name": "Emerging Leaders Program",
            "duration": "6 weeks",
            "format": "Fully online, self-paced",
            "certificate": "Yes, participation certificate",
            "mentors": ["David Wilson", "Jessica Brown"]
        }
    ],
    "general": [
        {
            "question": "How do I apply for a program?",
            "answer": "You can apply through our website by filling out the application form for your program of interest. Our team will review your application and contact you within 5-7 business days."
        },
        {
            "question": "Are scholarships available?",
            "answer": "Yes, we offer limited scholarships based on merit and financial need. Please indicate your interest in scholarship opportunities when applying."
        },
        {
            "question": "What is the time commitment for programs?",
            "answer": "Most programs require 4-6 hours per week, including live sessions, assignments, and group activities. Specific time commitments are detailed in each program description."
        }
    ]
}

mentor_data = [
    {
        "name": "Sarah Johnson",
        "role": "Leadership Coach",
        "bio": "With over 15 years of experience in executive coaching, Sarah specializes in helping women break through glass ceilings in corporate environments.",
        "expertise": ["Corporate Leadership", "Women Empowerment", "Career Transition"],
        "image": "👩‍💼"
    },
    {
        "name": "Robert Chen",
        "role": "Executive Advisor",
        "bio": "Former Fortune 500 executive who now dedicates his time to developing the next generation of leaders through practical, real-world strategies.",
        "expertise": ["Strategic Planning", "Change Management", "Executive Presence"],
        "image": "👨‍💼"
    },
    {
        "name": "Maria Rodriguez",
        "role": "Entrepreneurship Mentor",
        "bio": "Successful entrepreneur and investor who focuses on helping leaders build sustainable businesses with strong social impact.",
        "expertise": ["Entrepreneurship", "Social Impact", "Business Development"],
        "image": "👩‍🎓"
    }
]

# Set up Azure OpenAI
def setup_azure_openai():
    try:
        llm = AzureChatOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            temperature=0.7
        )
        return llm
    except Exception as e:
        st.error(f"Error initializing Azure OpenAI: {str(e)}")
        return None

# Initialize LLM
llm = setup_azure_openai()

# Function to get program information
def get_program_info(program_name=None):
    if program_name:
        for program in faq_data["programs"]:
            if program_name.lower() in program["name"].lower():
                return program
        return None
    else:
        return faq_data["programs"]

# Function to get FAQ answers
def get_faq_answer(question):
    for faq in faq_data["general"]:
        if faq["question"].lower() in question.lower():
            return faq["answer"]
    
    # If no direct match, use AI to generate response
    if llm:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant for Iron Lady Leadership Programs. Provide informative and encouraging responses about leadership development programs."),
                ("human", "Question: {question}\n\nContext about our programs: {program_info}\n\nPlease provide a helpful response:")
            ])
            
            chain = LLMChain(llm=llm, prompt=prompt)
            program_info = str(get_program_info())
            response = chain.run(question=question, program_info=program_info)
            return response
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"
    else:
        return "I'm sorry, I don't have information about that. Please contact our support team for assistance."

# Function to get mentor information
def get_mentor_info(mentor_name=None):
    if mentor_name:
        for mentor in mentor_data:
            if mentor_name.lower() in mentor["name"].lower():
                return mentor
        return None
    else:
        return mentor_data

# Function to handle user messages
def handle_user_message(user_input):
    # Convert to lowercase for easier matching
    input_lower = user_input.lower()
    
    # Check for program inquiries
    program_keywords = ["program", "course", "training", "women", "leadership", "executive"]
    if any(keyword in input_lower for keyword in program_keywords):
        programs = get_program_info()
        response = "We offer the following leadership programs:\n\n"
        for program in programs:
            response += f"**{program['name']}**\n"
            response += f"- Duration: {program['duration']}\n"
            response += f"- Format: {program['format']}\n"
            response += f"- Certificate: {program['certificate']}\n"
            response += f"- Mentors: {', '.join(program['mentors'])}\n\n"
        response += "Would you like more information about any specific program?"
        return response
    
    # Check for mentor inquiries
    mentor_keywords = ["mentor", "coach", "advisor", "teacher", "instructor"]
    if any(keyword in input_lower for keyword in mentor_keywords):
        mentors = get_mentor_info()
        response = "Our programs are led by experienced mentors:\n\n"
        for mentor in mentors:
            response += f"**{mentor['name']}** - {mentor['role']}\n"
            response += f"- Bio: {mentor['bio']}\n"
            response += f"- Expertise: {', '.join(mentor['expertise'])}\n\n"
        response += "Would you like to know more about any specific mentor?"
        return response
    
    # Check for application process
    application_keywords = ["apply", "application", "enroll", "register", "join"]
    if any(keyword in input_lower for keyword in application_keywords):
        return "To apply for any of our programs, please visit our website and fill out the application form for your program of interest. Our team will review your application and contact you within 5-7 business days. Would you like me to help you with any specific program application?"
    
    # Check for pricing information
    pricing_keywords = ["cost", "price", "fee", "tuition", "scholarship", "financial"]
    if any(keyword in input_lower for keyword in pricing_keywords):
        return "Program fees vary depending on the program length and format. We also offer scholarships based on merit and financial need. For specific pricing information and scholarship opportunities, please visit our website or contact our admissions team. Would you like information about a specific program?"
    
    # Default to FAQ system
    return get_faq_answer(user_input)

# Function to display chat message
def display_chat_message(role, message):
    with st.chat_message(role):
        st.markdown(message)

# Main application
def main():
    st.set_page_config(
        page_title="Iron Lady Chatbot",
        page_icon="👑",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage [data-testid="stMarkdownContainer"] {
        font-size: 1.1rem;
    }
    .header {
        background-color: #4B0082;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="header"><h1>👑 Iron Lady Leadership Chatbot</h1></div>', unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        st.header("About Iron Lady")
        st.write("We empower women through leadership development programs designed to build confidence, skills, and networks.")
        
        st.header("Our Programs")
        for program in get_program_info():
            with st.expander(program["name"]):
                st.write(f"**Duration:** {program['duration']}")
                st.write(f"**Format:** {program['format']}")
                st.write(f"**Certificate:** {program['certificate']}")
                st.write(f"**Mentors:** {', '.join(program['mentors'])}")
        
        st.header("Quick Links")
        if st.button("View All Programs"):
            st.session_state.conversation_history.append(("user", "Tell me about all programs"))
            st.session_state.conversation_history.append(("assistant", handle_user_message("Tell me about all programs")))
        
        if st.button("Meet Our Mentors"):
            st.session_state.conversation_history.append(("user", "Tell me about mentors"))
            st.session_state.conversation_history.append(("assistant", handle_user_message("Tell me about mentors")))
        
        if st.button("Application Process"):
            st.session_state.conversation_history.append(("user", "How do I apply?"))
            st.session_state.conversation_history.append(("assistant", handle_user_message("How do I apply?")))
    
    # Display conversation history
    for role, message in st.session_state.conversation_history:
        display_chat_message(role, message)
    
    # User input
    user_input = st.chat_input("Ask about our leadership programs...")
    
    if user_input:
        # Add user message to history
        st.session_state.conversation_history.append(("user", user_input))
        display_chat_message("user", user_input)
        
        # Get and display assistant response
        with st.spinner("Thinking..."):
            response = handle_user_message(user_input)
            st.session_state.conversation_history.append(("assistant", response))
            display_chat_message("assistant", response)
    
    # Add some suggested questions
    st.markdown("---")
    st.subheader("Suggested Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What programs do you offer?"):
            st.session_state.conversation_history.append(("user", "What programs do you offer?"))
            st.session_state.conversation_history.append(("assistant", handle_user_message("What programs do you offer?")))
            st.rerun()
    
    with col2:
        if st.button("Tell me about your mentors"):
            st.session_state.conversation_history.append(("user", "Tell me about your mentors"))
            st.session_state.conversation_history.append(("assistant", handle_user_message("Tell me about your mentors")))
            st.rerun()
    
    with col3:
        if st.button("How to apply for programs?"):
            st.session_state.conversation_history.append(("user", "How to apply for programs?"))
            st.session_state.conversation_history.append(("assistant", handle_user_message("How to apply for programs?")))
            st.rerun()

if __name__ == "__main__":
    main()