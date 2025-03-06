import streamlit as st
from datetime import datetime
from typing import Dict, List, Union
from src.data.database import crud

def chat_page():
    """Main chat interface page"""
    # If this is a new chat with no messages yet, initialize the chat session
    if not st.session_state.current_chat.get('messages'):
        initialize_chat_session()
        
    # Set up the layout with two columns (document sidebar and chat main)
    col1, col2 = st.columns([1, 4])
    
    with col1:
        document_sidebar()
    
    with col2:
        chat_main()

def document_sidebar():
    """Display the document sidebar with a scrollable list and fixed apply button"""
    st.markdown("""
    <style>
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 20%;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            background: var(--background-color);
            height: 100vh;  /* Full viewport height */
        }
        .document-list {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 1rem;
        }
        .apply-button {
            width: 100%;  /* Full width of the sidebar */
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar">', unsafe_allow_html=True)
    st.subheader("Document Selection")
    
    st.markdown('<div class="document-list">', unsafe_allow_html=True)
    
    files = get_combined_files()
    if 'selected_docs' not in st.session_state:
        st.session_state.selected_docs = set()
    
    for idx, file in enumerate(files):
        col1, col2 = st.columns([4, 1])
        with col1:
            checkbox_key = f"doc_{file['id']}_{idx}"
            selected = st.checkbox(
                file['name'],
                key=checkbox_key,
                value=file['id'] in st.session_state.selected_docs
            )
            if selected:
                st.session_state.selected_docs.add(file['id'])
            else:
                st.session_state.selected_docs.discard(file['id'])
        with col2:
            st.markdown(
                f"""<div class="status-indicator {'status-active' if file['active'] else 'status-inactive'}"></div>""",
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)  # Close document-list
    
    st.markdown('<div class="apply-button">', unsafe_allow_html=True)
    if st.button("Apply Selection", key="apply_selection_btn", use_container_width=True):
        update_document_status()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def chat_main():
    """Display the main chat area with messages and input"""
    # Add chat styling
    st.markdown("""
    <style>
        .chat-area {
            position: fixed;
            left: 20%;
            top: 0;
            bottom: 0;
            right: 0;
            display: flex;
            flex-direction: column;
            background: var(--background-color);
            height: 100vh;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }
        .input-container {
            padding: 1rem;
            background: var(--background-color);
            border-top: 1px solid var(--border-color);
        }
        .message {
            max-width: 70%;
            margin: 1rem 0;
            padding: 1rem;
            border-radius: 1rem;
            position: relative;
            line-height: 1.5;
        }
        .message.user {
            margin-left: auto;
            background-color: #007bff;
            color: white;
            border-bottom-right-radius: 0.2rem;
        }
        .message.ai {
            margin-right: auto;
            background-color: #e9ecef;
            color: black;
            border-bottom-left-radius: 0.2rem;
        }
        .chat-title {
            padding: 1rem;
            background-color: #121212;
            color: white;
            font-size: 1.25rem;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    
    # Add chat title with student name
    student_name = st.session_state.current_chat.get('student_data', {}).get('name', 'Student')
    st.markdown(f'<div class="chat-title">Talking to {student_name}</div>', unsafe_allow_html=True)
    
    # Display messages
    st.markdown('<div class="messages">', unsafe_allow_html=True)
    display_messages(st.session_state.current_chat.get('messages', []))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle message input and sending
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    col_input, col_send = st.columns([4, 1])

    with col_input:
        message = st.text_area(
            "Your message",
            key="message_input",
            height=80
        )
        
    with col_send:
        if st.button("Send", use_container_width=True):
            if message.strip():
                handle_send_message(message)
                # Use st.rerun() instead of experimental_rerun
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def display_messages(messages: List[Dict]):
    """Display chat messages with proper styling"""
    for msg in messages:
        with st.container():
            display_message(msg)

def display_message(message: Dict):
    """Display a single message with proper styling"""
    sender = message.get('sender', 'system')
    text = message.get('text', '')
    
    st.markdown(f"""
        <div class="message {sender}">
            {text}
        </div>
    """, unsafe_allow_html=True)

def handle_send_message(message: str):
    """Handle sending a new message"""
    if not message.strip():
        return
        
    # Add user message
    new_message = {
        "sender": "user",
        "text": message,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.current_chat['messages'].append(new_message)
    
    # Show typing indicator
    with st.spinner('AI is typing...'):
        # Get AI response
        ai_response = get_ai_response(message)
        if ai_response:
            ai_message = {
                "sender": "ai",
                "text": ai_response,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.current_chat['messages'].append(ai_message)
    
    # Update chat in session state
    update_chat_session()

def get_combined_files() -> List[Dict]:
    """Combine active and inactive files into one list with status"""
    try:
        active_files = crud.get_all_active_files()
        inactive_files = crud.get_all_inactive_files()
        
        # Add status to each file
        combined_files = [
            {**file, "active": True} for file in active_files
        ] + [
            {**file, "active": False} for file in inactive_files
        ]
        
        return combined_files
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return []

def update_document_status():
    """Update the active/inactive status of selected documents"""
    try:
        files = get_combined_files()
        for file in files:
            is_selected = file['id'] in st.session_state.selected_docs
            if is_selected and not file['active']:
                crud.move_file_to_active_by_id(file['id'])
            elif not is_selected and file['active']:
                crud.move_file_to_inactive_by_id(file['id'])
        st.success("Document selection updated!")
        st.rerun()
    except Exception as e:
        st.error(f"Error updating document status: {e}")

def get_documents() -> List[Dict]:
    """Get list of available documents"""
    if 'documents' not in st.session_state:
        st.session_state.documents = [
            {
                'id': '1',
                'name': 'Student Profile',
                'active': True,
                'content': lambda: st.session_state.current_chat['student_data']
            },
            {
                'id': '2',
                'name': 'Scenario Description',
                'active': True,
                'content': lambda: st.session_state.current_chat['scenario_data']
            }
        ]
    return st.session_state.documents

def get_ai_response(message: str) -> str:
    """Generate AI response based on user message and active context"""
    try:
        # Get active documents for context
        active_docs = [doc for doc in get_documents() if doc['active']]
        context = {}
        
        # Build context from active documents
        for doc in active_docs:
            if callable(doc['content']):
                context[doc['name']] = doc['content']()
        
        # TODO: Replace with actual AI call
        # Temporary placeholder response
        return f"AI Response: Acknowledging your message about {message[:30]}..."
    except Exception as e:
        st.error(f"Error generating AI response: {e}")
        return None

def update_chat_session():
    """Update the current chat session in session state"""
    try:
        # Find and update the chat in the chats list
        for idx, chat in enumerate(st.session_state.chats):
            if chat['id'] == st.session_state.current_chat['id']:
                st.session_state.chats[idx] = st.session_state.current_chat
                break
                
        # Update timestamp
        st.session_state.current_chat['updated_at'] = datetime.now().isoformat()
        
    except Exception as e:
        st.error(f"Error updating chat session: {e}")

def initialize_chat_session():
    """Initialize chat session without sending initial message"""
    if not st.session_state.current_chat.get('messages'):
        st.session_state.current_chat['messages'] = []