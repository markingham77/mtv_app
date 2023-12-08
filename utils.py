import datetime
import streamlit as st
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

def instantiate_initial_state():
    """
    sets a few variables up in streamlit's global session state

    this saves on writing boiler plate code like:

        if 'key' not in st.session_state:
            st.session_state['key'] = value
    """    

    if 'facets__yaxis_slider' not in st.session_state:
        st.session_state['facets__yaxis_slider'] = [None,None]

def save_value(key):
    st.session_state[key] = st.session_state["_"+key]
def get_value(key):
    st.session_state["_"+key] = st.session_state[key]

# get_value("my_key")
# st.number_input("Number of filters", key="_my_key", on_change=save_value, args="my_key")        