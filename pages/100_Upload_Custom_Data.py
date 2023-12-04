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
from utils import load_local_data


st.markdown('''
    <h1>Upload Your Custom Data</h1>
                        
    Your data will then be propogated across the app.

    Note that the app expects the data to be in the same format as the default data, see [here](https://git.lystit.com/markingham/timeseries_st_app/tree/main/data/example.csv)
            ''',unsafe_allow_html=True)


file_inputs_expander = st.expander("Data Inputs", expanded = True)
file_uploaded = None
file_type = file_inputs_expander.radio("File type", ('Remote file', 'Local file'))
if file_type == 'Local file':
    file_uploaded = file_inputs_expander.file_uploader('Upload your csv')
elif file_type ==  'Remote file':
    # url = file_inputs_expander.text_input(label='Enter a url (must point to a csv)',placeholder=examples[0]["file"])
    file_uploaded = file_inputs_expander.text_input(label='Enter a url (must point to a csv)')    

if (file_uploaded != None) & (file_uploaded!=''):
    # @st.cache_data
    df = pd.read_csv(file_uploaded, keep_default_na=False, na_values="")   
    df.columns = [c.upper() for c in df.columns]
    st.session_state['data'] = df

