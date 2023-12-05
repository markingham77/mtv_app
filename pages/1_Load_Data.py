import datetime
import streamlit as st
import plotly.express as px
import os
import pandas as pd
import numpy as np
import altair as alt
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from dateutil.parser import parse
from pathlib import Path
import pydqt
from pydqt import env_edit, set_snowflake_credentials
from utils import load_local_data, instantiate_initial_state, save_value, get_value
from streamlit_extras.app_logo import add_logo
from streamlit_sortables import sort_items

st.set_page_config(page_title="Timeseries Data Viewer",layout="wide")
add_logo("mtv_logo_bw.png",height=90)

st.markdown('''
    ### Load the data
   ##### To load the data, simply drag and drop the dimensions along which you want to split the data         
   ###### Please note that ordering impacts the order in which some data is displayed (eg in tree maps) but doesn't change what is loaded         
''')

if "dimensions" not in st.session_state:
    original_items = [
        {'header': 'Available Dimensions',  'items': ['REGION', 'TRAFFIC_SOURCE', 'LANDING_PAGE', 'USERSHIP']},
        {'header': 'Selected Dimensions', 'items': []}
    ]
else:
    all_dimensions = ['REGION', 'TRAFFIC_SOURCE', 'LANDING_PAGE', 'USERSHIP']
    original_dimensions = [x for x in all_dimensions if x not in st.session_state.dimensions]
    original_items = [
        {'header': 'Available Dimensions',  'items': original_dimensions},
        {'header': 'Selected Dimensions', 'items': st.session_state.dimensions}
    ]


sorted_items = sort_items(original_items, multi_containers=True)
st.session_state.dimensions = sorted_items[1]['items']

credentials = st.sidebar.expander('Snowflake Credentials', expanded=False)
dblogin=''
if "SNOWFLAKE_LOGIN" in os.environ:
    dblogin = os.environ["SNOWFLAKE_LOGIN"]    
dbrole=''
if "SNOWFLAKE_LOGIN" in os.environ:
    dbrole = os.environ["SNOWFLAKE_ROLE"]

if "disabled" not in st.session_state:
    st.session_state.disabled = True
def disable(a):
    st.session_state["disabled"] = a
def save_and_toggle(login,role):
    set_snowflake_credentials(login=login, role=role)
    if st.session_state.disabled:
        st.session_state.disabled = False
    else:
        st.session_state.disabled = True         
login = credentials.text_input('login',dblogin,help='Your Snowflake login (usually your email)', on_change=disable, args=(False,))
role = credentials.text_input('role',dbrole, help='Your role (this scopres out your privileges)', on_change=disable, args=(False,))
credentials.button('Save',disabled = st.session_state.disabled, on_click=save_and_toggle,args=(login,role))
