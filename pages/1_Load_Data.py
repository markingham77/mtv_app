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
from pydqt import env_edit
from utils import load_local_data, instantiate_initial_state, save_value, get_value
from streamlit_extras.app_logo import add_logo
from streamlit_sortables import sort_items

st.set_page_config(page_title="Timeseries Data Viewer",layout="wide")
add_logo("mtv_logo_bw.png",height=90)

st.markdown('''
   ### Drag and drop the dimensions along which you want to split the data         
   ###### Please note that ordering impacts the order in which some data is displayed (eg in tree maps)         
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