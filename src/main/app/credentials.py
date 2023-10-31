import streamlit as st

# local version will interact with dev database
# public version will interact with Production database
neo4j_credentials = st.secrets['neo4j_credentials']
