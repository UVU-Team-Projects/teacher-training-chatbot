import streamlit as st
import components.scenario_menu as scenario_menu

def main():
    st.header("Scenarios", divider="rainbow")
    scenario_menu.display()
