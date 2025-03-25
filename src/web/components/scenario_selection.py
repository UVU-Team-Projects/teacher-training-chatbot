import streamlit as st
import src.data.database.crud as db

class Scenario:
    next_id = 1
    def __init__(self, title, description, id=None):
        self.title = title
        self.description = description
        self.id = id if id is not None else Scenario.next_id
        if id is None:
            Scenario.next_id += 1

def do_back_button():
    st.session_state.create_chat_page = "student"

def select_scenario(scenario):
    st.session_state.selected_scenario = scenario
    st.session_state.page = "chat"

def load_scenarios():
    """Load scenarios from the database"""
    st.session_state.scenarios = []
    
    # Get scenarios from database
    db_scenarios = db.get_all_scenarios()
    
    # Create Scenario instances
    for db_scenario in db_scenarios:
        try:
            # Extract data from the database object
            title = db_scenario.title
            description = db_scenario.description
            scenario_id = db_scenario.id
            
            # Create Scenario instance and add to session state
            scenario = Scenario(title=title, description=description, id=scenario_id)
            st.session_state.scenarios.append(scenario)
            
            # Update next_id if needed
            if scenario_id >= Scenario.next_id:
                Scenario.next_id = scenario_id + 1
                
        except Exception as e:
            print(f"Error processing scenario: {e}")
            import traceback
            traceback.print_exc()
            continue

def delete_scenario(scenario):
    db.delete_scenario(scenario.id)

def edit_scenario(scenario):
    # TODO: Implement scenario editing
    print(f"Editing scenario: {scenario.title}")

def display_scenarios():
    # Display scenarios in a list of st.expander elements
    with st.container(border=True, height=400):
        if not st.session_state.scenarios:
            st.info("No scenarios available. Create a new scenario below.")
        else:
            for scenario in st.session_state.scenarios:
                with st.expander(scenario.title):
                    st.write(scenario.description)
                    select_col, edit_col, _, delete_col = st.columns([1, 1, 3, 1])
                    with select_col:
                        st.button("Select", 
                                on_click=select_scenario, 
                                args=(scenario,), 
                                key=f"{scenario.id}_select_button")
                    with edit_col:
                        st.button("Edit", 
                                on_click=edit_scenario,
                                args=(scenario,),
                                key=f"{scenario.id}_edit_button")
                    with delete_col:
                        st.button("Delete", 
                                on_click=delete_scenario,
                                args=(scenario,),
                                key=f"{scenario.id}_delete_button")

def create_scenario_form():
    # Create the form
    with st.expander("**Create New Scenario**"):
        with st.form(key="new_scenario_form"):
            new_scenario_title = st.text_input("Title*", help="Required")
            new_scenario_description = st.text_area("Description*", help="Required")
            submitted = st.form_submit_button("Create Scenario")
            
            # Check if form was submitted and required fields are not empty
            if submitted:
                if not new_scenario_title:
                    st.error("Title is required.")
                    return
                
                if not new_scenario_description:
                    st.error("Description is required.")
                    return
                
                # Create scenario in database
                new_db_scenario = db.create_scenario(
                    title=new_scenario_title,
                    description=new_scenario_description
                )
                
                if new_db_scenario:
                    st.success(f"Scenario '{new_scenario_title}' created!")
                    st.rerun()
                else:
                    st.error(f"Failed to create scenario '{new_scenario_title}'. It may already exist.")

def main():
    title, back = st.columns([9,1], vertical_alignment="bottom")
    with title:
        st.header("Please select a scenario.", divider="rainbow")
    with back:
        st.button("Back", on_click=do_back_button, key='scenario-back', use_container_width=True)

    load_scenarios()
    display_scenarios()
    create_scenario_form()
    
