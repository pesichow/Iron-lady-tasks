import streamlit as st
import json
import os
from datetime import datetime, timedelta
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import re

# Set up environment variables
os.environ["AZURE_OPENAI_API_KEY"] = "api key here"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://genaideployment.openai.azure.com"
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4o"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = -1

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

# Function to generate AI task suggestions
def generate_task_suggestions(user_context):
    if not llm:
        return ["Please check your Azure OpenAI configuration"]
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful productivity assistant. Suggest 3-5 specific, actionable tasks based on the user's context. Return the tasks as a JSON array of objects with 'title' and 'description' fields."),
            ("human", "User context: {context}\n\nPlease suggest relevant tasks:")
        ])
        
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(context=user_context)
        
        # Try to parse the response as JSON
        try:
            # Extract JSON from the response if it's wrapped in text
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions
            else:
                return [{"title": "Parse error", "description": "Could not parse AI response"}]
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response as a single suggestion
            return [{"title": "AI Suggestion", "description": response}]
            
    except Exception as e:
        return [{"title": "Error", "description": f"Failed to generate suggestions: {str(e)}"}]

# Function to summarize tasks
def summarize_tasks(tasks):
    if not llm:
        return "Please check your Azure OpenAI configuration"
    
    try:
        # Prepare task data for summarization
        task_data = "\n".join([f"{i+1}. {task['title']} - {task['description']} ({task['status']})" 
                              for i, task in enumerate(tasks)])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a productivity expert. Provide a concise summary (max 50 words) of these tasks, highlighting priorities and overall progress."),
            ("human", "Tasks:\n{task_data}\n\nSummary:")
        ])
        
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(task_data=task_data)
        return response
            
    except Exception as e:
        return f"Failed to generate summary: {str(e)}"

# Function to add a task
def add_task(title, description, priority, due_date=None, category="Personal"):
    new_task = {
        "id": len(st.session_state.tasks) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "due_date": due_date.strftime("%Y-%m-%d") if due_date else None,
        "completed_at": None
    }
    st.session_state.tasks.append(new_task)
    return new_task

# Function to update a task
def update_task(index, title, description, priority, due_date=None, category="Personal", status="Pending"):
    if 0 <= index < len(st.session_state.tasks):
        st.session_state.tasks[index]["title"] = title
        st.session_state.tasks[index]["description"] = description
        st.session_state.tasks[index]["priority"] = priority
        st.session_state.tasks[index]["category"] = category
        st.session_state.tasks[index]["due_date"] = due_date.strftime("%Y-%m-%d") if due_date else None
        st.session_state.tasks[index]["status"] = status
        
        if status == "Completed":
            st.session_state.tasks[index]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            st.session_state.tasks[index]["completed_at"] = None
            
        return True
    return False

# Function to delete a task
def delete_task(index):
    if 0 <= index < len(st.session_state.tasks):
        del st.session_state.tasks[index]
        return True
    return False

# Function to toggle task status
def toggle_task_status(index):
    if 0 <= index < len(st.session_state.tasks):
        if st.session_state.tasks[index]["status"] == "Pending":
            st.session_state.tasks[index]["status"] = "Completed"
            st.session_state.tasks[index]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            st.session_state.tasks[index]["status"] = "Pending"
            st.session_state.tasks[index]["completed_at"] = None
        return True
    return False

# Main application
def main():
    st.set_page_config(
        page_title="AI Task Manager",
        page_icon="✅",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .task-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4B0082;
    }
    .task-completed {
        border-left-color: #28a745 !important;
        opacity: 0.7;
    }
    .task-high {
        border-left-color: #dc3545 !important;
    }
    .task-medium {
        border-left-color: #ffc107 !important;
    }
    .task-low {
        border-left-color: #17a2b8 !important;
    }
    .header {
        background-color: #4B0082;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="header"><h1>✅ AI Task Manager</h1></div>', unsafe_allow_html=True)
    
    # Sidebar for task creation and AI features
    with st.sidebar:
        st.header("Add New Task")
        
        with st.form("task_form"):
            title = st.text_input("Task Title*", placeholder="Enter task title")
            description = st.text_area("Description", placeholder="Enter task description")
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            with col2:
                category = st.selectbox("Category", ["Work", "Personal", "Health", "Learning", "Other"])
            due_date = st.date_input("Due Date", min_value=datetime.now().date())
            
            submitted = st.form_submit_button("Add Task")
            if submitted:
                if title:
                    add_task(title, description, priority, due_date, category)
                    st.success("Task added successfully!")
                else:
                    st.error("Please provide a task title")
        
        st.markdown("---")
        st.header("AI Features")
        
        # AI task generation
        st.subheader("Generate Tasks with AI")
        context = st.text_area("Describe your goals or day:", placeholder="e.g., I need to prepare for my upcoming presentation, complete weekly reports, and schedule team meetings")
        
        if st.button("🤖 Generate Task Suggestions"):
            if context:
                with st.spinner("Generating AI suggestions..."):
                    st.session_state.ai_suggestions = generate_task_suggestions(context)
            else:
                st.warning("Please provide some context for AI suggestions")
        
        # Display AI suggestions
        if st.session_state.ai_suggestions:
            st.subheader("AI Suggestions")
            for i, suggestion in enumerate(st.session_state.ai_suggestions):
                with st.expander(f"Suggestion {i+1}: {suggestion.get('title', 'No title')}"):
                    st.write(suggestion.get('description', 'No description'))
                    if st.button(f"Add This Task", key=f"add_suggestion_{i}"):
                        add_task(
                            suggestion.get('title', 'AI Suggested Task'),
                            suggestion.get('description', ''),
                            "Medium",
                            None,
                            "AI Suggested"
                        )
                        st.success("Task added from suggestion!")
        
        # Task summary
        if st.session_state.tasks:
            st.markdown("---")
            if st.button("📊 Generate Summary"):
                summary = summarize_tasks(st.session_state.tasks)
                st.subheader("Task Summary")
                st.info(summary)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Your Tasks")
        
        # Filter options
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
        with col1b:
            filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
        with col1c:
            filter_category = st.selectbox("Filter by Category", ["All", "Work", "Personal", "Health", "Learning", "Other", "AI Suggested"])
        
        # Apply filters
        filtered_tasks = st.session_state.tasks
        if filter_status != "All":
            filtered_tasks = [t for t in filtered_tasks if t["status"] == filter_status]
        if filter_priority != "All":
            filtered_tasks = [t for t in filtered_tasks if t["priority"] == filter_priority]
        if filter_category != "All":
            filtered_tasks = [t for t in filtered_tasks if t["category"] == filter_category]
        
        # Display tasks
        if filtered_tasks:
            for i, task in enumerate(filtered_tasks):
                # Determine CSS class based on priority and status
                css_class = "task-card"
                if task["status"] == "Completed":
                    css_class += " task-completed"
                elif task["priority"] == "High":
                    css_class += " task-high"
                elif task["priority"] == "Medium":
                    css_class += " task-medium"
                else:
                    css_class += " task-low"
                
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                
                col2a, col2b = st.columns([4, 1])
                with col2a:
                    st.markdown(f"**{task['title']}**")
                    st.markdown(f"_{task['description']}_" if task['description'] else "*No description*")
                    st.caption(f"Category: {task['category']} | Priority: {task['priority']} | Created: {task['created_at']}")
                    if task['due_date']:
                        st.caption(f"Due: {task['due_date']}")
                    if task['completed_at']:
                        st.caption(f"Completed: {task['completed_at']}")
                
                with col2b:
                    # Toggle status button
                    status_text = "✓ Done" if task['status'] == "Pending" else "↻ Reopen"
                    if st.button(status_text, key=f"status_{i}"):
                        toggle_task_status(i)
                        st.rerun()
                    
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        delete_task(i)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No tasks found. Add some tasks using the sidebar!")
    
    with col2:
        st.header("Task Statistics")
        
        if st.session_state.tasks:
            # Calculate statistics
            total_tasks = len(st.session_state.tasks)
            completed_tasks = len([t for t in st.session_state.tasks if t["status"] == "Completed"])
            pending_tasks = total_tasks - completed_tasks
            
            high_priority = len([t for t in st.session_state.tasks if t["priority"] == "High"])
            medium_priority = len([t for t in st.session_state.tasks if t["priority"] == "Medium"])
            low_priority = len([t for t in st.session_state.tasks if t["priority"] == "Low"])
            
            # Display stats
            st.metric("Total Tasks", total_tasks)
            st.metric("Completed", completed_tasks)
            st.metric("Pending", pending_tasks)
            
            st.subheader("Priority Distribution")
            priority_data = {
                "High": high_priority,
                "Medium": medium_priority,
                "Low": low_priority
            }
            st.bar_chart(priority_data)
            
            st.subheader("Category Distribution")
            category_counts = {}
            for task in st.session_state.tasks:
                category = task["category"]
                category_counts[category] = category_counts.get(category, 0) + 1
            
            st.bar_chart(category_counts)
        else:
            st.info("No tasks to display statistics")
    
    # Edit task modal
    if st.session_state.edit_index >= 0 and st.session_state.edit_index < len(st.session_state.tasks):
        task = st.session_state.tasks[st.session_state.edit_index]
        
        with st.form("edit_form"):
            st.subheader("Edit Task")
            
            edit_title = st.text_input("Task Title", value=task["title"])
            edit_description = st.text_area("Description", value=task["description"])
            
            col3, col4 = st.columns(2)
            with col3:
                edit_priority = st.selectbox("Priority", ["High", "Medium", "Low"], 
                                           index=["High", "Medium", "Low"].index(task["priority"]))
            with col4:
                edit_category = st.selectbox("Category", ["Work", "Personal", "Health", "Learning", "Other", "AI Suggested"],
                                          index=["Work", "Personal", "Health", "Learning", "Other", "AI Suggested"].index(task["category"]))
            
            edit_due_date = st.date_input("Due Date", 
                                        value=datetime.strptime(task["due_date"], "%Y-%m-%d") if task["due_date"] else datetime.now().date(),
                                        min_value=datetime.now().date())
            
            edit_status = st.selectbox("Status", ["Pending", "Completed"], 
                                     index=0 if task["status"] == "Pending" else 1)
            
            col5, col6 = st.columns(2)
            with col5:
                if st.form_submit_button("Save Changes"):
                    update_task(
                        st.session_state.edit_index,
                        edit_title,
                        edit_description,
                        edit_priority,
                        edit_due_date,
                        edit_category,
                        edit_status
                    )
                    st.session_state.edit_index = -1
                    st.success("Task updated successfully!")
                    st.rerun()
            
            with col6:
                if st.form_submit_button("Cancel"):
                    st.session_state.edit_index = -1
                    st.rerun()

if __name__ == "__main__":
    main()

