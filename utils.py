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

@st.cache_data(persist="disk")
def load_sql_data(freq='month'):
    key = f'data_{freq}'
    if key not in st.session_state:
        q=pydqt.Query(f'''
            select * from core_wip.timeseries_{ freq }
            join core_wip.timeseries_lookup
            using (series_id)
            ;
            ''',
            freq=freq
        )
        q.load()

        # explode split_values
        cols = q.df['SPLITS'].values[0].split(',')
        df=q.df
        df[cols] = q.df['SPLIT_VALUES'].str.split(',',expand=True)
        columns = ['PERIOD_DS'] +  cols + ['METRIC','VALUE']
        df = df[columns]
        df = df.set_index(['PERIOD_DS'] +  cols)
        df = df.pivot(columns='METRIC',values='VALUE').reset_index()
        df.columns.name=''
        columns = df.columns
        new_columns=[]
        for c in columns:
            if c=='BUY2PI_RATE':
                new_columns.append('CONVERSION_RATE')
            elif c=='PI2SESSION_RATE':
                new_columns.append('LEAD_GEN_RATE')
            else:
                new_columns.append(c)
        df.columns = new_columns       
        df['PI_COUNT'] = df['LEAD_GEN_RATE']*df['SESSION_COUNT']/100
        df.columns.name=''

        st.session_state[key] = df
    else:
        df = st.session_state[key]
    return df



def load_local_data(freq='month'):
    key = f'data_{freq}'
    if key not in st.session_state:
        data = pd.read_csv(os.path.join(Path(__file__).parents[0],'data',f'mdv_{freq}.csv'))
        st.session_state[key] = data
    else:
        data = st.session_state[key]
    return data

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