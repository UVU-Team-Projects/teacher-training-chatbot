import streamlit as st
import src.data.database.crud as db

class Document:
    def __init__(self, title, active):
        # Trim title to max 40 chars and add ellipsis if needed
        self.original_title = title
        self.title = title if len(title) <= 40 else title[:25] + "..."
        self.active = active
        self.selected = False

def get_database_documents():
    # Empty documents in session state
    st.session_state.documents = []
    # Get active documents from database
    active = db.get_all_active_files()
    print(active)
    # Get inactive documents from database
    inactive = db.get_all_inactive_files()
    print(inactive)
    # Create Document instances for active and inactive documents.
    # Append them to st.session_state.documents
    for doc in active:
        st.session_state.documents.append(Document(doc["name"], True))
    for doc in inactive:
        st.session_state.documents.append(Document(doc["name"], False))

# Function to handle button click
def handle_revectorize():
    # Activate selected documents and deactivate others
    for i in range(len(st.session_state.documents)):
        if st.session_state.documents[i].title in st.session_state.selected_docs:
            if not st.session_state.documents[i].active:
                db.move_file_to_active_by_name(st.session_state.documents[i].original_title)
        else:
            if st.session_state.documents[i].active:
                db.move_file_to_inactive_by_name(st.session_state.documents[i].original_title)
    # TODO: CALL REVECTORIZE FUNCTION HERE!! Talk to ETHAN!


def main():
    get_database_documents()
    
    # Display document status
    st.header("Active Documents")
    # Check if there are any active documents
    active_docs_exist = any(doc.active for doc in st.session_state.documents)

    # Display message if no active documents
    if not active_docs_exist:
        st.write("No Active Document")
    else:
        for doc in st.session_state.documents:
            if doc.active:
                st.write(doc.title)
                    
    # Store document titles for selection
    doc_titles = [doc.original_title for doc in st.session_state.documents]
    
    # Get currently selected documents
    if "selected_docs" not in st.session_state:
        st.session_state.selected_docs = []


    # Display documents with pill selection for multi-select
    st.header("Revectorize")
    selected_docs = st.multiselect(
        "Select documents to include in vectorization.",
        doc_titles
    )
    
    # Update session state with selection
    st.session_state.selected_docs = selected_docs
    
    # Button to toggle activation based on selection
    st.button("Revectorize", on_click=handle_revectorize)
