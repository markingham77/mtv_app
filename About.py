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
from streamlit_extras.app_logo import add_logo

st.set_page_config(page_title="Metric Tree Viewer",layout="wide")
add_logo("mtv_logo_bw.png",height=90)


# st.title('Multi-Dimensional Data Viewer (MD<sup>2</sup>V)')
st.markdown('''
# MTV - Metric Tree Viewer

A Streamlit app which allows you to look at the various metrics which feed into Net Commission:

- Session Counts
- Lead Generation Rate (LGR)
- Track Counts
- Track Conversion Rate (TCR)
- Average Order Value (AOV)
- Order Counts
- Commission Rate (CPA)

MTV consists of various sub-apps which allow you to analyse the above metric across various dimensions and time:

- Facets
    - timeseries plots of the above metrics across multiple dimenions, such as: region, traffic source and others

- Tree Maps
    - tree plots of count-like metric by hierarchical dimensions

- Data Table
    - table of raw data with multiple controls to drill down and summarise            
''',unsafe_allow_html=True)
