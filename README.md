# Iron-lady-tasks
ron Lady Chatbot & AI To-Do Manager
Tools/Tech Stack Used
Python 3.8+

Streamlit for interactive web UI

Azure OpenAI GPT-4o via langchain_openai for AI-powered natural language understanding and generation

LangChain for simplified prompt management and chaining AI calls

Standard libraries: os, json, datetime, re

How to Run the Code
Clone or download the project files.

Install dependencies:

bash
pip install streamlit langchain langchain-openai
Set up Azure OpenAI environment variables in the code (already included in the scripts):

AZURE_OPENAI_API_KEY

AZURE_OPENAI_ENDPOINT

AZURE_OPENAI_DEPLOYMENT

AZURE_OPENAI_API_VERSION

Run each app:

For Iron Lady Chatbot:

bash
streamlit run ironlady_chatbot.py
For AI To-Do Manager:

bash
streamlit run ai_todo_manager.py
Open the local URL provided by Streamlit in your browser.

Features Implemented
Task 1: Iron Lady Leadership Chatbot
FAQ-based chatbot with predefined program and mentor data.

Azure OpenAI integration for natural language fallback responses.

Multi-turn chat support with session memory.

Sidebar with quick info and suggested questions.

Task 2: AI To-Do Manager
Full CRUD (Create, Read, Update, Delete) for tasks with title, description, priority, category, and due date.

Interactive UI with filters by status, priority, and category.

AI-powered task suggestions generated from user context using Azure OpenAI.

Task summarization feature to provide concise updates.

Color-coded task cards for easy priority/status recognition.
