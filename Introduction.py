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
from utils import load_local_data, instantiate_initial_state



st.set_page_config(page_title="Timeseries Data Viewer",layout="wide")
# st.title('Multi-Dimensional Data Viewer (MD<sup>2</sup>V)')
st.markdown('''
    <h1>Timeseries Data Viewer</h1>
                        
    A multi page app which examines various operating and financial metrics across time and other dimensions.
    The app works straight out of the box with pre-specified data but if you want to examine your own custom data then you can upload from the sidebar.
            ''',unsafe_allow_html=True)
